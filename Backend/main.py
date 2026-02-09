# main.py
import os
# Enable CrewAI tracing programmatically so traces are collected
os.environ.setdefault('CREWAI_TRACING_ENABLED', 'true')
from crewai import Crew
import logging
import sys
from datetime import datetime
import re

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Ensure output directory exists for final artifacts
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure logger to write to a timestamped file and keep console output
log_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = os.path.join(LOG_DIR, f"maljrs_{log_ts}.log")
logger = logging.getLogger("maljrs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a raw terminal text log (preserves original terminal formatting)
raw_txt_path = os.path.join(LOG_DIR, f"terminal_{log_ts}.txt")
raw_log_file = open(raw_txt_path, "a", encoding="utf-8")

# Load banner from banner.txt file
banner_path = os.path.join(os.path.dirname(__file__), "banner.txt")
try:
    with open(banner_path, "r", encoding="utf-8") as f:
        banner = "\n" + f.read() + "\n\n"
except FileNotFoundError:
    # Fallback banner if banner.txt not found
    banner = (
        "\n╔" + "═" * 58 + "╗\n"
        "║" + " " * 58 + "║\n"
        "║" + "              MALJRS - Multi-Agent Legal Assistant              " + "║\n"
        "║" + " " * 58 + "║\n"
        "╚" + "═" * 58 + "╝\n\n"
    )

# Write banner to both the structured log and raw terminal log
logger.info(banner)
try:
    raw_log_file.write(banner)
    raw_log_file.flush()
except Exception:
    pass


# Simple metrics collector for internal usage and JSON output
class Metrics:
    def __init__(self):
        self.llm_calls = []
        self.errors = []
        self.start_time = datetime.now().isoformat()

    def log_llm_call(self, model, prompt_len, response_len, duration, success):
        self.llm_calls.append({
            "model": model,
            "prompt_len": prompt_len,
            "response_len": response_len,
            "duration": duration,
            "success": bool(success),
            "ts": datetime.now().isoformat(),
        })

    def log_error(self, code, message, where=None):
        self.errors.append({
            "code": code,
            "message": message,
            "where": where,
            "ts": datetime.now().isoformat(),
        })

    def save(self, path=None):
        import json
        try:
            metrics_path = path or os.path.join(OUTPUT_DIR, f"metrics_{log_ts}.json")
            with open(metrics_path, "w", encoding="utf-8") as f:
                json.dump({
                    "start_time": self.start_time,
                    "llm_calls": self.llm_calls,
                    "errors": self.errors,
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("Failed to save metrics")


# Instantiate global metrics before agents import so LLMs can record into it
metrics = Metrics()

# ANSI escape code pattern for stripping color codes
ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi_codes(text):
    """Remove ANSI color codes from text for clean file output."""
    return ANSI_ESCAPE_PATTERN.sub('', text)

# Helper to mirror stdout/stderr to logger while preserving console
class StreamToLogger:
    def __init__(self, logger, level, stream, raw_file=None):
        self.logger = logger
        self.level = level
        self.stream = stream
        self.raw_file = raw_file

    def write(self, buf):
        if not buf:
            return
        try:
            # Strip ANSI codes for structured logging
            text = strip_ansi_codes(buf).rstrip('\n')
            if text:
                for line in text.splitlines():
                    self.logger.log(self.level, line)
        except Exception:
            pass
        try:
            # Write cleaned buffer to terminal log file (without ANSI codes)
            if self.raw_file:
                try:
                    cleaned_buf = strip_ansi_codes(buf)
                    self.raw_file.write(cleaned_buf)
                    self.raw_file.flush()
                except Exception:
                    pass
            # Write original buffer with ANSI codes to console for color display
            self.stream.write(buf)
        except Exception:
            pass

    def flush(self):
        try:
            self.stream.flush()
        except Exception:
            pass

# Replace sys.stdout/stderr so prints and uncaught traces are also logged
sys.stdout = StreamToLogger(logger, logging.INFO, sys.__stdout__, raw_file=raw_log_file)
sys.stderr = StreamToLogger(logger, logging.ERROR, sys.__stderr__, raw_file=raw_log_file)

# Compatibility shim for CrewAI tool config
try:
    from langchain.tools import StructuredTool
    from crewai_tools import tool as crewai_tool_module
    
    for mod in [StructuredTool, crewai_tool_module]:
        if hasattr(mod, 'StructuredTool'):
            current = mod.StructuredTool._run
            # Avoid double-wrapping
            if getattr(current, '__is_shim__', False):
                continue

            orig = current

            def _run_wrapper(self, *args, config=None, **kwargs):
                if config is None:
                    class _DummyConfig:
                        pass
                    config = _DummyConfig()
                return orig(self, *args, config=config, **kwargs)

            # mark to avoid re-wrapping
            _run_wrapper.__is_shim__ = True
            mod.StructuredTool._run = _run_wrapper
except Exception:
    pass

from agents import CIVIL_AGENTS, CRIMINAL_AGENTS, SHARED_AGENTS, CLASSIFIER_AGENT
from tasks import create_classifier_task, create_civil_tasks, create_criminal_tasks, create_shared_tasks
import time
import json


def run_legal_crew(victim_input: str):
    # Step 1: Classify
    print("🔍 Step 1/4: Classifying case type...")
    classifier_task = create_classifier_task(victim_input)
    classifier_crew = Crew(agents=[CLASSIFIER_AGENT], tasks=[classifier_task], verbose=False)
    
    start = time.time()
    try:
        result = str(classifier_crew.kickoff()).strip()
        # Try to extract classification from JSON response or fallback to keyword search
        case_type = "civil"
        result_lower = result.lower()
        if "criminal" in result_lower:
            case_type = "criminal"
        elif "civil" in result_lower:
            case_type = "civil"
        # Try parsing JSON if present
        try:
            import re
            json_match = re.search(r'\{[^{}]*"classification"[^{}]*\}', result, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                case_type = parsed.get("classification", case_type)
        except:
            pass
    except Exception as e:
        logger.exception("Classifier failed")
        raise
    dur = time.time() - start
    logger.info("Classifier completed in %.2fs - Result: %s", dur, case_type)
    # save classifier output for debugging
    try:
        with open(os.path.join(LOG_DIR, "classifier_output.json"), "w", encoding="utf-8") as f:
            json.dump({"input": victim_input, "output": result, "extracted_type": case_type}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    print(f"✅ Case Type: {case_type.upper()} (completed in {dur:.1f}s)\n")

    # Step 2 & 3: Combined Analysis
    print(f"📋 Step 2 & 3: Comprehensive Legal Analysis ({case_type.capitalize()} Track)...")
    print("   • Analyzing Facts & Laws")
    print("   • Finding Precedents (Parallel)")
    print("   • Constitutional Review (Parallel)")
    print("   • Synthesizing Pathway & Report")
    
    if case_type == "civil":
        track_agents = CIVIL_AGENTS
        track_tasks = create_civil_tasks(victim_input)
    else:
        track_agents = CRIMINAL_AGENTS
        track_tasks = create_criminal_tasks(victim_input)
    
    # Set up context dependencies for efficient information flow
    if len(track_tasks) >= 2:
        track_tasks[1].context = [track_tasks[0]]  # Law mapper depends on fact interpreter
    if len(track_tasks) >= 3:
        track_tasks[2].context = [track_tasks[0], track_tasks[1]]  # Precedent finder depends on both
        track_tasks[2].async_execution = True # Run in parallel with constitutional validator

    # We pass empty string for track_output as it is not used in task descriptions, 
    # relying on context instead.
    shared_tasks = create_shared_tasks("", case_type)
    
    # Set up context dependencies
    if len(shared_tasks) >= 1:
        # Constitutional Validator depends on facts and laws
        shared_tasks[0].context = [track_tasks[0], track_tasks[1]]
        shared_tasks[0].async_execution = True # Run in parallel with precedent finder

    if len(shared_tasks) >= 2:
        # Pathway advisor depends on constitutional validator and laws
        shared_tasks[1].context = [shared_tasks[0], track_tasks[1]]
    
    if len(shared_tasks) >= 3:
        # Report synthesizer depends on ALL previous tasks
        shared_tasks[2].context = track_tasks + [shared_tasks[0], shared_tasks[1]]
    
    # Combine into a single crew for optimized execution
    all_agents = track_agents + SHARED_AGENTS
    all_tasks = track_tasks + shared_tasks
    
    analysis_crew = Crew(agents=all_agents, tasks=all_tasks, verbose=False)
    start = time.time()
    try:
        final_report = analysis_crew.kickoff()
    except Exception as e:
        logger.exception("Analysis failed")
        raise
    dur = time.time() - start
    logger.info("Full analysis completed in %.2fs", dur)
    
    # Save intermediate outputs for debugging (optional)
    try:
        with open(os.path.join(LOG_DIR, "track_output.txt"), "w", encoding="utf-8") as f:
            f.write(str(final_report))
    except Exception:
        pass
    print(f"✅ Analysis complete (completed in {dur:.1f}s)\n")
    
    # Step 4: Save outputs
    print("💾 Step 4/4: Saving final report...")
    try:
        # persist final report to the output folder
        out_path = os.path.join(OUTPUT_DIR, f"final_report_{log_ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(final_report))
        logger.info("Final report saved to %s", out_path)
        print(f"✅ Report saved to: {out_path}\n")
        # save structured metrics
        try:
            metrics.save()
        except Exception:
            logger.exception("Failed saving metrics")
    except Exception:
        logger.exception("Failed saving final report to output")

    return final_report


if __name__ == "__main__":
    # Tracing has been enabled programmatically for this run
    print("Tracing enabled: CREWAI_TRACING_ENABLED=true")
    print("⚖️  Multi-Agent Legal Assistant (India)")
    print("Describe your issue in simple English (e.g., 'My husband abused me and left'):\n")
    
    victim_story = input("> ")
    print("\n⏳ Analyzing your case...\n")
    
    try:
        report = run_legal_crew(victim_story)
        print("\n" + "="*60)
        print("📄 YOUR LEGAL REPORT")
        print("="*60)
        print(report)
    finally:
        try:
            metrics.save()
        except Exception:
            logger.exception("Failed saving metrics at shutdown")
        try:
            raw_log_file.close()
        except Exception:
            pass
