interface Props {
  lowConfidenceCount: number;
  totalCount: number;
}
export default function ConfidenceAlert({ lowConfidenceCount, totalCount }: Props) {
  if (totalCount === 0 || lowConfidenceCount === 0) {
    return (
      <div className="bg-neutral-900 border border-emerald-800/50 rounded-2xl p-4 flex items-center gap-3">
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
        <span className="text-neutral-300 text-sm">No low-confidence responses in the current window.</span>
      </div>
    );
  }
  const pct = Math.round((lowConfidenceCount / totalCount) * 100);
  return (
    <div className="bg-neutral-900 border border-red-800/50 rounded-2xl p-4 flex items-center gap-3">
      <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
      <span className="text-neutral-200 text-sm">
        <strong className="text-red-400">{lowConfidenceCount}</strong> of {totalCount} queries ({pct}%) fell below the confidence threshold.
      </span>
    </div>
  );
}
