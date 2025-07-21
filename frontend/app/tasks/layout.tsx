export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <main className="h-full w-full bg-background">{children}</main>;
}
