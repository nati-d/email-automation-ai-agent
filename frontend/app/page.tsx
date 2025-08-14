"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useApp } from "@/components/AppContext";
import { LoginDialog } from "@/components/LoginDialog";
import {
  Mail,
  Bot,
  Tags,
  CheckSquare,
  PenTool,
  BarChart3,
  Star,
  Users,
  Shield,
  Zap,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  Menu,
  X,
  Play,
} from "lucide-react";
import { WaitlistForm } from "@/components/WaitlistForm";

export default function LandingPage() {
  const { user } = useApp();
  const router = useRouter();
  const [isYearly, setIsYearly] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (user) {
      router.push("/dashboard");
    }
  }, [user, router]);

  // Don't render landing page if user is authenticated (while redirecting)
  if (user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  const features = [
    {
      icon: Mail,
      title: "Email Aggregation",
      description:
        "Connect Gmail, Outlook, Yahoo and more. One unified inbox for all your accounts.",
    },
    {
      icon: Tags,
      title: "Smart Categorization",
      description:
        "AI automatically sorts emails into custom categories like Work, Bank, Personal, and more.",
    },
    {
      icon: CheckSquare,
      title: "Task Extraction",
      description:
        "Never miss a deadline. AI extracts tasks and action items from your emails automatically.",
    },
    {
      icon: PenTool,
      title: "AI Compose",
      description:
        "Write emails in your personal tone. AI learns your style and helps compose professional responses.",
    },
    {
      icon: Bot,
      title: "Conversational AI Bot",
      description:
        "Ask questions like 'What did John say last week?' and get instant, contextual answers.",
    },
    {
      icon: BarChart3,
      title: "Email Summarization",
      description:
        "Get clean previews of long email threads. Save time with AI-powered summaries.",
    },
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Startup Founder",
      avatar: "SC",
      quote:
        "This AI assistant cleared 200+ unread emails in 10 minutes. Complete game changer for my productivity.",
    },
    {
      name: "Marcus Rodriguez",
      role: "Executive Assistant",
      avatar: "MR",
      quote:
        "The task extraction feature alone saves me 2 hours daily. It's like having a personal email secretary.",
    },
    {
      name: "Emily Watson",
      role: "Product Manager",
      avatar: "EW",
      quote:
        "Finally, an inbox that works for me instead of against me. The AI categorization is incredibly accurate.",
    },
  ];

  const faqs = [
    {
      question: "Can I trust the AI with my data?",
      answer:
        "Yes, absolutely. All data is encrypted with AES-256 encryption and we follow strict GDPR compliance. Your emails are processed securely and never stored permanently on our servers.",
    },
    {
      question: "Which email providers do you support?",
      answer:
        "We support Gmail, Outlook, Yahoo Mail, Apple Mail, and most IMAP/POP3 email providers. You can connect multiple accounts from different providers.",
    },
    {
      question: "How accurate is the AI categorization?",
      answer:
        "Our AI achieves 95%+ accuracy in email categorization. It learns from your preferences and gets better over time. You can always manually adjust categories to improve accuracy.",
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer:
        "Yes, you can cancel your subscription at any time. There are no long-term contracts or cancellation fees. Your data remains accessible during your billing period.",
    },
    {
      question: "Is there a mobile app?",
      answer:
        "Yes! Our web app is fully responsive and works great on mobile. We also have native iOS and Android apps coming soon.",
    },
  ];

  const plans = [
    {
      name: "Free",
      price: { monthly: 0, yearly: 0 },
      description: "Perfect for trying out AI email management",
      features: [
        "1 email account",
        "Basic categorization",
        "Daily task extraction",
        "5 AI compositions per month",
        "Email summaries",
      ],
      cta: "Get Started Free",
      popular: false,
    },
    {
      name: "Pro",
      price: { monthly: 8, yearly: 6 },
      description: "For professionals who live in their inbox",
      features: [
        "Unlimited email accounts",
        "Advanced AI categorization",
        "Unlimited task extraction",
        "Unlimited AI compositions",
        "Conversational AI bot",
        "Priority support",
      ],
      cta: "Start Pro Trial",
      popular: true,
    },
    {
      name: "Team",
      price: { monthly: 20, yearly: 16 },
      description: "For teams that need shared email intelligence",
      features: [
        "Everything in Pro",
        "Team task sharing",
        "Admin dashboard",
        "Team analytics",
        "Custom integrations",
        "Dedicated support",
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Mail className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">AlphaMail</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Features
              </a>
              <a
                href="#pricing"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Pricing
              </a>
              <a
                href="#waitlist"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Waitlist
              </a>
              <a
                href="#faq"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                FAQ
              </a>
              <Button
                variant="outline"
                className="mr-2"
                onClick={() => setLoginDialogOpen(true)}
              >
                Login
              </Button>
              <Button
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                onClick={() => setLoginDialogOpen(true)}
              >
                Try Free
              </Button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </Button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <div className="flex flex-col space-y-4">
                <a
                  href="#features"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Features
                </a>
                <a
                  href="#pricing"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Pricing
                </a>
                <a
                  href="#waitlist"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Waitlist
                </a>
                <a
                  href="#faq"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  FAQ
                </a>
                <div className="flex flex-col space-y-2 pt-4 border-t border-gray-200">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setLoginDialogOpen(true)}
                  >
                    Login
                  </Button>
                  <Button
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                    onClick={() => setLoginDialogOpen(true)}
                  >
                    Try Free
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden min-h-screen flex items-center">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
          {/* Floating Orbs */}
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-40 right-20 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-2000"></div>

          {/* Grid Pattern */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            {/* Animated Badge */}
            <div className="inline-flex items-center gap-2 mb-8 px-4 py-2 bg-white/80 backdrop-blur-sm border border-blue-200 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 group">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-blue-700">
                Now powered by Google Gemini
              </span>
              <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center group-hover:rotate-12 transition-transform duration-300">
                <Zap className="w-3 h-3 text-white" />
              </div>
            </div>

            {/* Main Headline with Typing Animation */}
            <div className="mb-8">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-4 leading-tight">
                <span className="block mb-2">Reclaim Your</span>
                <span className="block bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent animate-gradient-x">
                  Inbox Freedom
                </span>
              </h1>
              <div className="h-1 w-32 bg-gradient-to-r from-blue-500 to-indigo-500 mx-auto rounded-full"></div>
            </div>

            {/* Subtitle with Fade-in Animation */}
            <p className="text-xl sm:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed font-light">
              Transform email chaos into{" "}
              <span className="font-semibold text-gray-800">
                organized productivity
              </span>{" "}
              with AI that organizes, summarizes, and writes your emails
              intelligently.
            </p>

            {/* CTA Buttons with Hover Effects */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
              <Button
                size="lg"
                className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                onClick={() => {
                  document
                    .getElementById("waitlist")
                    ?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                <span className="relative z-10 flex items-center">
                  Join Waitlist
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-indigo-700 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </Button>

              <Button
                size="lg"
                variant="outline"
                className="group px-8 py-4 border-2 border-gray-300 hover:border-blue-500 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                <Play className="mr-2 w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                Watch Demo
              </Button>
            </div>

            {/* Enhanced Hero Mockup */}
            <div className="relative max-w-6xl mx-auto">
              {/* Floating Elements */}
              <div className="absolute -top-8 -left-8 w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl rotate-12 opacity-80 animate-bounce delay-300"></div>
              <div className="absolute -top-4 -right-12 w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full opacity-80 animate-bounce delay-700"></div>
              <div className="absolute -bottom-6 -left-6 w-20 h-20 bg-gradient-to-r from-green-500 to-teal-500 rounded-3xl rotate-45 opacity-80 animate-bounce delay-1000"></div>

              {/* Main Dashboard Mockup */}
              <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 overflow-hidden transform hover:scale-[1.02] transition-transform duration-500">
                {/* Browser Header */}
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-red-400 rounded-full hover:bg-red-500 transition-colors cursor-pointer"></div>
                        <div className="w-3 h-3 bg-yellow-400 rounded-full hover:bg-yellow-500 transition-colors cursor-pointer"></div>
                        <div className="w-3 h-3 bg-green-400 rounded-full hover:bg-green-500 transition-colors cursor-pointer"></div>
                      </div>
                      <div className="text-sm font-medium text-gray-600 ml-4">
                        AlphaMail Dashboard
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-xs text-gray-500">Live</span>
                    </div>
                  </div>
                </div>

                {/* Dashboard Content */}
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Email List */}
                    <div className="lg:col-span-2 space-y-4">
                      {/* Email Item 1 */}
                      <div className="group flex items-center space-x-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-l-4 border-blue-500 hover:shadow-lg transition-all duration-300 cursor-pointer">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                          <Mail className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            Meeting Follow-up
                          </div>
                          <div className="text-sm text-gray-600">
                            AI categorized as Work • 2 min ago
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span className="text-xs text-blue-600 font-medium">
                            High Priority
                          </span>
                        </div>
                      </div>

                      {/* Email Item 2 */}
                      <div className="group flex items-center space-x-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border-l-4 border-green-500 hover:shadow-lg transition-all duration-300 cursor-pointer">
                        <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                          <CheckSquare className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
                            Task: Review proposal by Friday
                          </div>
                          <div className="text-sm text-gray-600">
                            Extracted from email • Due in 2 days
                          </div>
                        </div>
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      </div>

                      {/* Email Item 3 */}
                      <div className="group flex items-center space-x-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl border-l-4 border-purple-500 hover:shadow-lg transition-all duration-300 cursor-pointer">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                          <Tags className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                            Client Proposal Draft
                          </div>
                          <div className="text-sm text-gray-600">
                            AI suggested improvements • 1 hour ago
                          </div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        </div>
                      </div>
                    </div>

                    {/* AI Assistant Panel */}
                    <div className="bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 rounded-2xl p-6 border border-indigo-200/50 hover:shadow-xl transition-all duration-300">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center">
                          <Bot className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <span className="font-semibold text-indigo-900">
                            AI Assistant
                          </span>
                          <div className="flex items-center space-x-1 mt-1">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            <span className="text-xs text-indigo-600">
                              Online
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="bg-white/80 rounded-xl p-3 text-sm text-indigo-800 leading-relaxed">
                          "I found{" "}
                          <span className="font-semibold text-indigo-900">
                            3 urgent emails
                          </span>{" "}
                          and created{" "}
                          <span className="font-semibold text-indigo-900">
                            2 tasks
                          </span>{" "}
                          for you."
                        </div>
                        <div className="bg-white/80 rounded-xl p-3 text-sm text-indigo-800 leading-relaxed">
                          "Would you like me to draft a response to the client
                          inquiry?"
                        </div>

                        <div className="flex space-x-2 mt-4">
                          <Button
                            size="sm"
                            className="bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg flex-1"
                          >
                            Yes, Draft It
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-indigo-300 text-indigo-600 rounded-lg"
                          >
                            Later
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Stats Bar */}
                  <div className="mt-8 grid grid-cols-3 gap-6">
                    <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl">
                      <div className="text-2xl font-bold text-blue-600">
                        247
                      </div>
                      <div className="text-sm text-gray-600">
                        Emails Organized
                      </div>
                    </div>
                    <div className="text-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                      <div className="text-2xl font-bold text-green-600">
                        18
                      </div>
                      <div className="text-sm text-gray-600">Tasks Created</div>
                    </div>
                    <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
                      <div className="text-2xl font-bold text-purple-600">
                        5.2h
                      </div>
                      <div className="text-sm text-gray-600">Time Saved</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-gray-400 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </section>

      {/* Security & Privacy Section */}
      <section id="security" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Security & Privacy
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AlphaMail is designed with security first: strong encryption,
              privacy-preserving architecture, and clear controls over your
              data.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl">Encryption Everywhere</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  TLS in transit. Encrypted storage at rest where applicable.
                  Sensitive tokens are scoped and never exposed to clients.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl">Account-Level Access</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  OAuth-based authentication with least-privilege scopes. Only
                  your accounts are accessible to you.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                  <CheckSquare className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl">Privacy Controls</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  Clear data controls. Export or delete your data on request.
                  Configurable retention for summaries and drafts.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl">Reliable by Design</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  Monitored infrastructure, secure defaults, and routine
                  updates. Built for availability and safety.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Email Mastery
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI doesn't just manage your emails—it transforms how you work
              with them.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300"
              >
                <CardHeader>
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            See AlphaMail in Action
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Watch how our AI transforms a cluttered inbox into an organized,
            actionable workspace in minutes.
          </p>
          <Button size="lg" variant="secondary" className="group">
            <Play className="mr-2 w-5 h-5 group-hover:scale-110 transition-transform" />
            Watch 2-Minute Demo
          </Button>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Choose the plan that fits your email volume and team size.
            </p>

            {/* Pricing Toggle */}
            <div className="flex items-center justify-center space-x-4 mb-8">
              <span
                className={`text-sm ${
                  !isYearly ? "text-gray-900 font-medium" : "text-gray-500"
                }`}
              >
                Monthly
              </span>
              <button
                onClick={() => setIsYearly(!isYearly)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isYearly ? "bg-blue-600" : "bg-gray-200"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isYearly ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
              <span
                className={`text-sm ${
                  isYearly ? "text-gray-900 font-medium" : "text-gray-500"
                }`}
              >
                Yearly
              </span>
              {isYearly && (
                <Badge className="bg-green-100 text-green-700">Save 25%</Badge>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <Card
                key={index}
                className={`relative ${
                  plan.popular
                    ? "border-blue-500 shadow-xl scale-105"
                    : "border-gray-200"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-600 text-white">
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">
                      ${isYearly ? plan.price.yearly : plan.price.monthly}
                    </span>
                    <span className="text-gray-500">
                      {plan.price.monthly === 0 ? "" : "/month"}
                    </span>
                  </div>
                  <CardDescription className="mt-2">
                    {plan.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, featureIndex) => (
                      <li
                        key={featureIndex}
                        className="flex items-center space-x-3"
                      >
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className={`w-full ${
                      plan.popular
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                        : ""
                    }`}
                    variant={plan.popular ? "default" : "outline"}
                    onClick={() => setLoginDialogOpen(true)}
                  >
                    {plan.cta}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Loved by Professionals Worldwide
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands who've transformed their email experience.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 fill-yellow-400 text-yellow-400"
                      />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-6 italic">
                    "{testimonial.quote}"
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white font-medium">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        {testimonial.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {testimonial.role}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Waitlist Section */}
      <section
        id="waitlist"
        className="py-20 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Ready to Transform Your Email Experience?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Join thousands of professionals waiting for early access to
              AlphaMail. Be among the first to experience the future of email
              management.
            </p>
          </div>

          <WaitlistForm />
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about AlphaMail.
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <Card key={index} className="border-0 shadow-sm">
                <CardContent className="p-0">
                  <button
                    onClick={() => setOpenFaq(openFaq === index ? null : index)}
                    className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-medium text-gray-900">
                      {faq.question}
                    </span>
                    {openFaq === index ? (
                      <ChevronUp className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    )}
                  </button>
                  {openFaq === index && (
                    <div className="px-6 pb-4">
                      <p className="text-gray-600">{faq.answer}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Email Experience?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of professionals who've already reclaimed their
            inbox.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              variant="secondary"
              className="group"
              onClick={() => setLoginDialogOpen(true)}
            >
              Start Free Trial
              <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-blue-600"
            >
              Schedule Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">AlphaMail</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                Transform your email chaos into organized productivity with
                Gemini-powered email management.
              </p>
              <div className="flex space-x-4">
                <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 cursor-pointer transition-colors">
                  <span className="text-xs">𝕏</span>
                </div>
                <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 cursor-pointer transition-colors">
                  <span className="text-xs">in</span>
                </div>
                <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 cursor-pointer transition-colors">
                  <span className="text-xs">f</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a
                    href="#features"
                    className="hover:text-white transition-colors"
                  >
                    Features
                  </a>
                </li>
                <li>
                  <a
                    href="#pricing"
                    className="hover:text-white transition-colors"
                  >
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Integrations
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    API
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Terms of Service
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 AlphaMail.io. All rights reserved.
              </p>
              <div className="flex items-center space-x-4 mt-4 md:mt-0">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
                />
                <Button
                  size="sm"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  Subscribe
                </Button>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Login Dialog */}
      <LoginDialog open={loginDialogOpen} onOpenChange={setLoginDialogOpen} />
    </div>
  );
}
