import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system/legacy";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { unzipSync, strFromU8 } from "fflate";
import { toByteArray } from "base64-js";
import { XMLParser } from "fast-xml-parser";

const STORAGE_PREFIX = "health_daily:";
const LAST_SYNCED_KEY = "health_last_synced_at";

type DailySummary = {
  steps: number;
  active_kcal: number;
  basal_kcal: number;
  sleep_minutes: number;
};

// Apple Health identifiers for sleep analysis
const SLEEP_CATEGORY_TYPE = "HKCategoryTypeIdentifierSleepAnalysis";
const SLEEP_VALUE_PREFIX_ASLEEP = "HKCategoryValueSleepAnalysisAsleep"; // covers Asleep, AsleepUnspecified, AsleepCore, AsleepDeep, AsleepREM
const SLEEP_VALUE_IN_BED = "HKCategoryValueSleepAnalysisInBed";

function toISODateLocal(date: Date): string {
  const y = date.getFullYear();
  const m = `${date.getMonth() + 1}`.padStart(2, "0");
  const d = `${date.getDate()}`.padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function parseAppleHealthDate(dateStr: string | undefined): Date | null {
  if (!dateStr) return null;
  const dNative = new Date(dateStr);
  if (!isNaN(dNative.getTime())) return dNative;
  const matchTz = dateStr.match(
    /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2}) ([-+]\d{4})$/
  );
  if (matchTz) {
    const [, datePart, timePart, tz] = matchTz;
    const tzWithColon = `${tz.slice(0, 3)}:${tz.slice(3)}`;
    const iso = `${datePart}T${timePart}${tzWithColon}`;
    const d = new Date(iso);
    if (!isNaN(d.getTime())) return d;
  }
  const matchNoTz = dateStr.match(
    /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})$/
  );
  if (matchNoTz) {
    const [, datePart, timePart] = matchNoTz;
    const d = new Date(`${datePart}T${timePart}`);
    if (!isNaN(d.getTime())) return d;
  }
  console.warn("[HealthImport] Unparseable date:", dateStr);
  return null;
}

export async function importHealthZip(): Promise<
  { days: number } | { error: string }
> {
  const pick = await DocumentPicker.getDocumentAsync({
    type: "application/zip",
    multiple: false,
    copyToCacheDirectory: true,
  });
  if (pick.canceled || !pick.assets?.[0]) return { error: "Canceled" };

  const asset = pick.assets[0];
  const fileUri = asset.uri;
  try {
    const bin = await FileSystem.readAsStringAsync(fileUri, {
      encoding: "base64",
    });
    const zipData = toByteArray(bin);
    const files = unzipSync(zipData);

    // Apple export contains export.xml at root
    const exportXmlEntry = Object.keys(files).find((k) =>
      k.endsWith("export.xml")
    );
    if (!exportXmlEntry) return { error: "export.xml not found in zip" };

    const xml = strFromU8(files[exportXmlEntry]);
    const parser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: "",
      parseAttributeValue: true,
      trimValues: true,
    });

    const stepsByDay: Record<string, number> = {};
    const activeByDay: Record<string, number> = {};
    const basalByDay: Record<string, number> = {};
    const sleepAsleepByDay: Record<string, number> = {};
    const sleepInBedByDay: Record<string, number> = {};

    const root = parser.parse(xml);
    const recordsRaw = root?.HealthData?.Record ?? [];
    const records: any[] = Array.isArray(recordsRaw)
      ? recordsRaw
      : [recordsRaw];

    for (const rec of records) {
      const type = rec?.type as string | undefined;
      const startDateStr = rec?.startDate as string | undefined;
      if (!type || !startDateStr) continue;
      const endDateStr = rec?.endDate as string | undefined;
      const valueNum =
        typeof rec?.value === "number"
          ? rec.value
          : parseFloat(rec?.value ?? "0");
      const valueStr =
        typeof rec?.value === "string" ? (rec.value as string) : undefined;

      const start = parseAppleHealthDate(startDateStr);
      if (!start) continue;
      const end = parseAppleHealthDate(endDateStr) || start;
      const value = isNaN(valueNum) ? 0 : valueNum;

      if (type === "HKQuantityTypeIdentifierStepCount") {
        const day = toISODateLocal(start);
        stepsByDay[day] = (stepsByDay[day] || 0) + value;
        continue;
      }
      if (type === "HKQuantityTypeIdentifierActiveEnergyBurned") {
        const day = toISODateLocal(start);
        activeByDay[day] = (activeByDay[day] || 0) + value;
        continue;
      }
      if (type === "HKQuantityTypeIdentifierBasalEnergyBurned") {
        const day = toISODateLocal(start);
        basalByDay[day] = (basalByDay[day] || 0) + value;
        continue;
      }
      if (type === SLEEP_CATEGORY_TYPE) {
        const v = valueStr ?? "";
        const isAsleep = v.startsWith(SLEEP_VALUE_PREFIX_ASLEEP);
        const isInBed = v === SLEEP_VALUE_IN_BED;
        // Numeric fallback: 0 = InBed, 1 = Asleep, 2 = Awake
        const isAsleepNumeric = !v && value === 1;
        const isInBedNumeric = !v && value === 0;
        if (!isAsleep && !isInBed && !isAsleepNumeric && !isInBedNumeric) {
          // Unknown/awake → ignore
          continue;
        }
        let cursor = new Date(start);
        while (cursor < end) {
          const dayEnd = new Date(
            cursor.getFullYear(),
            cursor.getMonth(),
            cursor.getDate(),
            23,
            59,
            59,
            999
          );
          const segStart = cursor;
          const segEnd = end < dayEnd ? end : dayEnd;
          const minutes = Math.max(
            0,
            (segEnd.getTime() - segStart.getTime()) / 60000
          );
          const dayISO = toISODateLocal(segStart);
          if (isAsleep || isAsleepNumeric) {
            sleepAsleepByDay[dayISO] =
              (sleepAsleepByDay[dayISO] || 0) + minutes;
          } else if (isInBed || isInBedNumeric) {
            sleepInBedByDay[dayISO] = (sleepInBedByDay[dayISO] || 0) + minutes;
          }
          cursor = new Date(dayEnd.getTime() + 1);
        }
      }
    }

    const allDays = new Set<string>([
      ...Object.keys(stepsByDay),
      ...Object.keys(activeByDay),
      ...Object.keys(basalByDay),
      ...Object.keys(sleepAsleepByDay),
      ...Object.keys(sleepInBedByDay),
    ]);

    for (const day of allDays) {
      const sleepMinutes =
        (sleepAsleepByDay[day] ?? 0) > 0
          ? sleepAsleepByDay[day]
          : (sleepInBedByDay[day] ?? 0);
      const summary: DailySummary = {
        steps: stepsByDay[day] ?? 0,
        active_kcal: activeByDay[day] ?? 0,
        basal_kcal: basalByDay[day] ?? 0,
        sleep_minutes: sleepMinutes,
      };
      await AsyncStorage.setItem(
        `${STORAGE_PREFIX}${day}`,
        JSON.stringify(summary)
      );
      console.log("[HealthImport] Saved", `${STORAGE_PREFIX}${day}`, summary);
    }
    const nowIso = new Date().toISOString();
    await AsyncStorage.setItem(LAST_SYNCED_KEY, nowIso);
    console.log(
      `[HealthImport] Import complete. Days saved: ${allDays.size}. Last synced at ${nowIso}`
    );

    return { days: allDays.size };
  } catch (e: any) {
    return { error: e?.message || "Import failed" };
  }
}
