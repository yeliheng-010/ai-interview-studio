import { render, screen } from "@testing-library/react";

import { EmptyState } from "@/components/empty-state";

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(<EmptyState title="暂无数据" description="请先上传一份简历。" />);

    expect(screen.getByText("暂无数据")).toBeInTheDocument();
    expect(screen.getByText("请先上传一份简历。")).toBeInTheDocument();
  });
});
