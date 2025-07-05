import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function Landing() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md text-center p-8 shadow-xl">
        <CardContent>
          <h1 className="text-3xl font-bold mb-4">AI SaaS Factory</h1>
          <p className="text-muted-foreground mb-6">
            Turn any idea into a live SaaS product—no code required.
          </p>
          <Button asChild size="lg">
            <a href="/signup">Get Started</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
} 