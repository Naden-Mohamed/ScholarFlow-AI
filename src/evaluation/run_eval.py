import asyncio, argparse, json, datetime
from controllers.EvaluationController import evaluate_rag
from evaluation.metrics.generation_metrics import run_ragas_eval

async def main(mode:str):
    
    retrieval_results, generation_samples = await evaluate_rag()

    report = {"timestamp": datetime.datetime.utcnow().isoformat(), "retrieved": retrieval_results}

    if mode == "generation_eval":
        report["generation"] = run_ragas_eval(generation_samples)

    out_path = f"src/evaluation/reports/eval_{report['timestamp']}.json"

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report written to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generation_eval", "retreival_eval"], default="retreival_eval")
    args = parser.parse_args()
    asyncio.run(main(args.mode))
