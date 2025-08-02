import { WorkbenchAuthProvider } from '@/contexts/WorkbenchAuthContext';

export default function WorkbenchLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <WorkbenchAuthProvider>
      {children}
    </WorkbenchAuthProvider>
  );
}