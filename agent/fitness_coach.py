"""
AI Fitness Coach module.

Core AI coaching logic with MCP tools and knowledge base integration.
"""

import asyncio
import os
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from knowledge import KnowledgeBase
from mcp_integration import MCPIntegration

try:
    from langchain_ollama import ChatOllama  # Fallback if OpenAI not configured
except Exception:
    ChatOllama = None  # type: ignore


class FitnessCoach:
    """AI Fitness Coach with MCP tools and knowledge base integration."""

    def __init__(self, model_name: str = "gpt-5-nano"):
        """Initialize the AI Fitness Coach."""
        self.model_name = model_name
        # Prefer hosted OpenAI GPT-5 nano; prepare fallback Ollama model
        self.model = None
        self.fallback_model = None
        self._context_dir = None  # set during setup_knowledge_base
        openai_key = os.getenv("OPENAI_API_KEY")
        warned_openai_missing = False
        warned_ollama_missing = False

        def is_ollama_name(name: str) -> bool:
            lname = name.lower()
            return ":" in lname or lname.startswith(
                ("qwen", "llama", "mistral", "phi", "mixtral", "codellama", "gemma")
            )

        def init_openai(name: str):
            nonlocal warned_openai_missing
            if not openai_key:
                if not warned_openai_missing:
                    print(
                        "⚠️ OPENAI_API_KEY not set; skipping OpenAI model initialization."
                    )
                    warned_openai_missing = True
                return None
            try:
                return ChatOpenAI(model=name, temperature=0.7)
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI model '{name}': {e}")
                return None

        def init_ollama(name: str):
            nonlocal warned_ollama_missing
            if ChatOllama is None:
                if not warned_ollama_missing:
                    print(
                        "⚠️ langchain_ollama not available; skipping Ollama model initialization."
                    )
                    warned_ollama_missing = True
                return None
            try:
                return ChatOllama(model=name, temperature=0.7)
            except Exception as e:
                print(f"⚠️ Failed to initialize Ollama model '{name}': {e}")
                return None

        requested_is_ollama = is_ollama_name(model_name)
        candidate_order = []

        if requested_is_ollama:
            candidate_order.append(("ollama", init_ollama, model_name))
            if ChatOllama is not None:
                ollama_fallback_name = "qwen2.5:3b"
                if ollama_fallback_name != model_name:
                    candidate_order.append(
                        ("ollama", init_ollama, ollama_fallback_name)
                    )
            if openai_key:
                candidate_order.append(("openai", init_openai, "gpt-5-nano"))
        else:
            candidate_order.append(("openai", init_openai, model_name))
            if openai_key and model_name != "gpt-5-nano":
                candidate_order.append(("openai", init_openai, "gpt-5-nano"))
            if ChatOllama is not None:
                candidate_order.append(("ollama", init_ollama, "qwen2.5:3b"))

        attempt_results = {}
        primary_selection = None

        for provider, initializer, name in candidate_order:
            key = (provider, name)
            if key in attempt_results:
                model_instance = attempt_results[key]
            else:
                model_instance = initializer(name)
                attempt_results[key] = model_instance
            if model_instance is not None:
                self.model = model_instance
                self.model_name = name
                primary_selection = key
                break

        if self.model is None:
            raise RuntimeError(
                "No LLM available. Set OPENAI_API_KEY or install/run Ollama."
            )

        for provider, initializer, name in candidate_order:
            key = (provider, name)
            if key == primary_selection:
                continue
            if key in attempt_results:
                model_instance = attempt_results[key]
            else:
                model_instance = initializer(name)
                attempt_results[key] = model_instance
            if model_instance is not None:
                self.fallback_model = model_instance
                break

        if self.model_name != model_name:
            print(
                f"ℹ️ Using fallback model '{self.model_name}' instead of requested '{model_name}'."
            )

        # If still no primary model, use whichever fallback worked
        if self.model is None and self.fallback_model is not None:
            self.model = self.fallback_model
        if self.model is None:
            raise RuntimeError(
                "No LLM available. Set OPENAI_API_KEY or install/run Ollama."
            )
        self.knowledge_base = KnowledgeBase()
        self.mcp = MCPIntegration()
        self.agent = None

        # Initialize the prompt template
        self._setup_prompt_template()

    def _setup_prompt_template(self) -> None:
        """Set up the prompt template for the AI coach."""
        self.template = """
You are a minimalist fitness coach expert focused on evidence-based, time-efficient workout planning.

RESEARCH CONTEXT:
{context}

SOURCES:
{sources}

USER REQUEST:
{input}

INSTRUCTIONS:
- Provide helpful, evidence-based fitness advice and workout recommendations
- When creating workout plans, use the available MCP tools to fetch workout history, create routines, and manage workout data
- Always analyze user's training patterns before making recommendations
- Focus on progressive overload, proper recovery, and balanced muscle group development
- Use exercise templates and create structured routines when appropriate
- Present plans clearly with rationale for exercise selection and programming decisions
- Cite relevant sources by name when applicable; avoid fabricating citations

Available tools:
- get_workouts: Fetch user's workout history
- create_routine: Create new workout routines
- create_routine_folder: Organize routines into folders
- get_exercise_templates: Access exercise database
- And other workout management tools

Provide comprehensive, actionable fitness guidance.
"""

        self.prompt = ChatPromptTemplate.from_template(self.template)

    def setup_knowledge_base(self, context_dir: str) -> bool:
        """Set up the knowledge base from context directory."""
        return self.knowledge_base.setup_knowledge_base(context_dir)

    async def setup_agent(self) -> bool:
        """Set up the LangGraph agent with MCP tools."""
        try:
            # Test MCP connection first
            connection_ok = await self.mcp.test_connection()
            if not connection_ok:
                print("⚠️ MCP connection failed, agent will use knowledge base only")
                return False

            # Load tools and create agent
            tools = await self.mcp.load_tools()
            if tools:
                self.agent = self.mcp.create_agent(self.model)
                if self.agent:
                    print("✅ Agent successfully created with MCP tools")
                    return True

            print("⚠️ Failed to create agent with MCP tools")
            return False
        except Exception as e:
            print(f"⚠️ Error setting up agent: {e}")
            return False

    def _build_rag_context(
        self, user_input: str, seed_queries: List[str] | None = None
    ) -> Tuple[str, List[str]]:
        """Build a richer RAG context by running multiple diversified queries and summarizing results.

        Returns a tuple of (summary_text, source_filenames).
        """
        retriever = self.knowledge_base.get_retriever()
        if not retriever:
            return "", []

        # Create diversified queries
        base_queries = [
            user_input,
            f"{user_input} evidence-based guidelines",
            f"{user_input} programming principles: volume intensity frequency",
            f"{user_input} minimalist training and compound movements",
        ]
        if seed_queries:
            base_queries.extend(seed_queries)

        seen_snippets = set()
        collected_docs = []
        for q in list(dict.fromkeys(base_queries))[:8]:
            try:
                docs = retriever.invoke(q)
            except Exception as e:
                print(f"⚠️ Retrieval failed for query '{q}': {e}")
                continue
            for d in docs or []:
                # Deduplicate by content prefix and source when available
                snippet_key = (
                    d.page_content[:200],
                    d.metadata.get("source", "unknown"),
                )
                if snippet_key in seen_snippets:
                    continue
                seen_snippets.add(snippet_key)
                collected_docs.append(d)

        if not collected_docs:
            return "", []

        # Format docs and collect sources
        formatted_text, sources = self.knowledge_base.format_docs_with_sources(
            collected_docs[:12]
        )

        # Summarize into a concise context
        try:
            summary_prompt = ChatPromptTemplate.from_template(
                """
Summarize the following excerpts into a concise, evidence-focused brief to assist with the user's request.
Emphasize actionable principles, programming guidance, and key tradeoffs. Keep it under 300 words.

USER REQUEST:
{question}

EXCERPTS:
{docs}
"""
            )
            chain = summary_prompt | self.model | StrOutputParser()
            summary = chain.invoke({"question": user_input, "docs": formatted_text})
        except Exception as e:
            print(f"⚠️ Summarization failed: {e}")
            # Fallback: return truncated concatenation
            summary = formatted_text[:1500]

        return summary, sources

    async def get_response(self, user_input: str) -> str:
        """Get a response from the AI coach."""
        # Build improved RAG context
        context_text, sources = self._build_rag_context(user_input)
        sources_text = ", ".join(sources) if sources else ""

        if self.agent:
            try:
                # Use agent with MCP tools
                agent_input = user_input
                if context_text or sources_text:
                    agent_input = f"RESEARCH CONTEXT:\n{context_text}\n\nSOURCES:\n{sources_text}\n\nUSER REQUEST: {user_input}"
                print(
                    "\n📝 Prompt (LLM input via Agent)\n=================================================="
                )
                print(agent_input)
                print("==================================================\n")
                response = await self.agent.ainvoke(
                    {"messages": [("user", agent_input)]}
                )
                if isinstance(response, dict) and "messages" in response:
                    messages = response["messages"]
                    if messages and hasattr(messages[-1], "content"):
                        return messages[-1].content
                return str(response)
            except Exception as e:
                print(f"⚠️ Agent error: {e}, falling back to knowledge base")

        # Fallback to basic chain with knowledge base context
        def try_invoke(llm_model):
            chain = self.prompt | llm_model | StrOutputParser()
            rendered_prompt_text = self.template.format(
                context=context_text, sources=sources_text, input=user_input
            )
            print(
                "\n📝 Prompt (LLM input)\n=================================================="
            )
            print(rendered_prompt_text)
            print("==================================================\n")
            return chain.invoke(
                {"context": context_text, "sources": sources_text, "input": user_input}
            )

        try:
            return try_invoke(self.model)
        except Exception as e1:
            print(f"⚠️ RAG+LLM failed: {e1}. Trying fallback model...")
            if self.fallback_model is not None:
                try:
                    return try_invoke(self.fallback_model)
                except Exception as e3:
                    print(f"⚠️ Fallback model failed: {e3}")
            return "Sorry, I'm temporarily unavailable due to rate limits. Please try again shortly."

    async def generate_weekly_plan(self) -> str:
        """Generate a comprehensive weekly workout plan."""
        # Build research context specialized for weekly planning
        research_context, sources = self._build_rag_context(
            "weekly minimalist training plan",
            seed_queries=[
                "minimalist training weekly workout plan",
                "training volume and frequency for compound lifts",
                "evidence-based programming: progressive overload and recovery",
            ],
        )
        sources_text = ", ".join(sources) if sources else ""

        weekly_plan_prompt = f"""
Create a weekly workout plan for me. Follow these steps:

1. Get available exercises: get_exercise_templates(page=1, pageSize=100)

2. Fetch my last 10 workouts: get_workouts(pageSize=10)

3. Analyze the workouts to find:
   - Which muscle groups I train most/least
   - Any weak points or imbalances
   - Training patterns and frequency

4. Create a minimalist weekly plan that:
   - Uses compound movements (squats, rdls, bench press etc)
   - Balances all muscle groups
   - Includes progressive overload
   - Uses exercise templates from step 1

5. Create the routine folder: create_routine_folder(payload={{"routine_folder": {{"title": "Week xx"}}}})

6. Create workout routines for each day using this complete payload format:
create_routine(payload={{"routine": {{
  "title": "Push Day Workout",
  "folder_id": folder_id_from_step_5,
  "notes": "Minimalist push workout",
  "exercises": [
    {{
      "exercise_template_id": "05293BCA",
      "notes": "Focus on form",
      "rest_seconds": 120,
      "sets": [
        {{"reps": 5, "weight": 100}},
        {{"reps": 5, "weight": 105}},
        {{"reps": 5, "weight": 110}}
      ]
    }},
    {{
      "exercise_template_id": "12345ABC",
      "notes": "Progressive overload",
      "rest_seconds": 90,
      "sets": [
        {{"reps": 8, "weight": 50}},
        {{"reps": 8, "weight": 55}},
        {{"reps": 8, "weight": 60}}
      ]
    }}
  ]
}}}})

RESEARCH CONTEXT:
{research_context if research_context else "Use general evidence-based principles"}

SOURCES:
{sources_text}
"""
        return await self.get_response(weekly_plan_prompt)

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        mcp_stats = self.mcp.get_stats()
        return {
            "model_name": self.model_name,
            "has_retriever": self.knowledge_base.has_knowledge_base(),
            "has_agent": self.agent is not None,
            **mcp_stats,
        }
