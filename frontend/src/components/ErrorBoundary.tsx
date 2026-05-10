import { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

export default function ErrorBoundary({ children }: Props) {
  return <>{children}</>;
}
