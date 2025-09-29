import React from "react";
import { Platform, TextInput, type TextInputProps } from "react-native";

import { cn } from "@/lib/utils";

type TextareaProps = TextInputProps & {
  className?: string;
  placeholderClassName?: string;
  unstyled?: boolean;
};

const Textarea = React.forwardRef<TextInput, TextareaProps>(
  (
    {
      className,
      multiline = true,
      numberOfLines = Platform.select({ web: 2, native: 8 }), // On web, numberOfLines also determines initial height. On native, it determines the maximum height.
      placeholderClassName,
      unstyled = false,
      editable,
      textAlignVertical = "top",
      ...props
    },
    ref
  ) => {
    return (
      <TextInput
        ref={ref}
        className={cn(
          !unstyled &&
            "text-foreground border-input dark:bg-input/30 flex min-h-16 w-full flex-row rounded-md border bg-transparent px-3 py-2 text-base shadow-sm shadow-black/5 md:text-sm",
          !unstyled &&
            Platform.select({
              web: "placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive field-sizing-content resize-y outline-none transition-[color,box-shadow] focus-visible:ring-[3px] disabled:cursor-not-allowed",
            }),
          editable === false && "opacity-50",
          className
        )}
        placeholderClassName={cn(
          !unstyled && "text-muted-foreground",
          placeholderClassName
        )}
        multiline={multiline}
        numberOfLines={numberOfLines}
        editable={editable}
        textAlignVertical={textAlignVertical}
        {...props}
      />
    );
  }
);

Textarea.displayName = "Textarea";

export { Textarea };
