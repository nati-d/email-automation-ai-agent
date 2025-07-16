import { AuthGuard } from "@/components/auth/auth-guard";
import { EmailLayout } from "@/components/email/email-layout";

export default function Home() {
  return (
    <AuthGuard>
      <EmailLayout />
    </AuthGuard>
  );
}
