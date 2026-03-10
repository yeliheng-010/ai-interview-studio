import { ReactNode } from "react";

export function PageHeader({
  kicker,
  title,
  subtitle,
  actions
}: {
  kicker: string;
  title: string;
  subtitle: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 border-b border-line pb-5 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="section-kicker">{kicker}</p>
        <h2 className="display-font mt-3 text-3xl">{title}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 muted-text">{subtitle}</p>
      </div>
      {actions ? <div>{actions}</div> : null}
    </div>
  );
}
