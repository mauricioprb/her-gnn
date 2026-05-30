import { useQuery } from "@tanstack/vue-query";
import { fetchComparisonPredictions } from "@/api";

export function useComparisonPredictions() {
  return useQuery({
    queryKey: ["comparison", "predictions"],
    queryFn: fetchComparisonPredictions,
    staleTime: Infinity,
  });
}
