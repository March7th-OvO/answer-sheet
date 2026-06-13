type ResultPanelProps = {
  loading: boolean;
  error: string;
  pdfUrl: string;
  layoutJsonUrl: string;
};

export function ResultPanel({ loading, error, pdfUrl, layoutJsonUrl }: ResultPanelProps) {
  return (
    <section className="panel">
      <h2>结果下载</h2>
      {loading ? <p>生成中...</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
      {!loading && !error && !pdfUrl && !layoutJsonUrl ? <p>生成完成后将在这里显示下载链接。</p> : null}
      {pdfUrl ? (
        <a href={pdfUrl} target="_blank" rel="noreferrer">
          下载 PDF
        </a>
      ) : null}
      {layoutJsonUrl ? (
        <a href={layoutJsonUrl} target="_blank" rel="noreferrer">
          下载 layout.json
        </a>
      ) : null}
    </section>
  );
}
