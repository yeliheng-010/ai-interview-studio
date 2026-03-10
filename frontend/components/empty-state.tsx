import { ReactNode } from "react";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="paper-panel rounded-[28px] border-dashed p-10 text-center">
      <p className="section-kicker">Empty State</p>
      <h3 className="display-font mt-3 text-3xl">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm muted-text">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
