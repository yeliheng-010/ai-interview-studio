export function LoadingPanel({ text = "正在加载..." }: { text?: string }) {
  return (
    <div className="paper-panel rounded-[28px] p-8 text-center">
      <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-line border-t-accent" />
      <p className="text-sm muted-text">{text}</p>
    </div>
  );
}
