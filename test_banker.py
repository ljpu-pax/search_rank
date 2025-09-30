#!/usr/bin/env python3
"""Test banker query evaluation."""

from search_pipeline import SearchPipeline
import json

def main():
    print("="*60)
    print("TESTING BANKER QUERY")
    print("="*60)

    # Initialize pipeline
    pipeline = SearchPipeline(
        use_reranking=True,
        use_enhanced_reranker=True,
        initial_k=100,
        final_k=10
    )

    # Run evaluation
    config_path = "queries/bankers.yml"

    try:
        evaluation = pipeline.evaluate_query(config_path)

        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        print(json.dumps(evaluation, indent=2))

        # Print summary
        if "average_final_score" in evaluation:
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            print(f"Average Final Score: {evaluation['average_final_score']}")
            print(f"Number of Candidates: {evaluation['num_candidates']}")

            print("\nHard Criteria (Pass Rates):")
            for hard in evaluation.get("average_hard_scores", []):
                print(f"  - {hard['criteria_name']}: {hard['pass_rate']*100:.0f}%")

            print("\nSoft Criteria (Average Scores):")
            for soft in evaluation.get("average_soft_scores", []):
                print(f"  - {soft['criteria_name']}: {soft['average_score']:.2f}/10")

    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
