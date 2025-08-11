"use client"

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Mail, 
  User, 
  MessageSquare, 
  Users, 
  CheckCircle, 
  Loader2,
  Clock,
  Star
} from "lucide-react";
import { joinWaitlist, checkWaitlistStatus, type WaitlistEntry, type WaitlistJoinResponse } from "@/lib/api/waitlist";

interface WaitlistFormProps {
  onSuccess?: (response: WaitlistJoinResponse) => void;
  className?: string;
}

export function WaitlistForm({ onSuccess, className = "" }: WaitlistFormProps) {
  const [formData, setFormData] = useState<WaitlistEntry>({
    email: "",
    name: "",
    use_case: "",
    referral_source: ""
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<WaitlistJoinResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof WaitlistEntry, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email) {
      setError("Email is required");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await joinWaitlist(formData);
      setSuccess(response);
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "Failed to join waitlist";
      if (errorMessage.includes("already registered")) {
        setError("This email is already registered in our waitlist!");
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Card className={`max-w-2xl mx-auto ${className}`}>
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl text-green-800">Welcome to the Waitlist!</CardTitle>
          <CardDescription className="text-lg">
            {success.message}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Success Info */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 text-center">
            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600">{success.total_entries.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Total Signups</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">✓</div>
                <div className="text-sm text-gray-600">You're In!</div>
              </div>
            </div>
          </div>

          {/* Next Steps */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-800 flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              What happens next?
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                <span>We'll email you when early access is available</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                <span>We'll contact you as soon as we're ready</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                <span>Share with friends to help us grow!</span>
              </li>
            </ul>
          </div>

          {/* Social Share */}
          <div className="text-center pt-4 border-t">
            <p className="text-sm text-gray-600 mb-3">Help us spread the word!</p>
            <div className="flex justify-center space-x-3">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  const text = "I just joined the EmailAI waitlist! 🚀 AI-powered email management is coming soon.";
                  const url = window.location.origin;
                  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
                }}
              >
                Share on Twitter
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  navigator.clipboard.writeText(window.location.origin);
                  // You could add a toast notification here
                }}
              >
                Copy Link
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`max-w-2xl mx-auto ${className}`}>
      <CardHeader className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
            <Mail className="w-6 h-6 text-white" />
          </div>
          <Badge className="bg-green-100 text-green-700">
            Join the waitlist
          </Badge>
        </div>
        <CardTitle className="text-2xl">Get Early Access to EmailAI</CardTitle>
        <CardDescription className="text-lg">
          Be among the first to experience AI-powered email management. Join thousands of others waiting for early access.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email - Required */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium flex items-center">
              <Mail className="w-4 h-4 mr-2" />
              Email Address *
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="your@email.com"
              required
              className="w-full"
            />
          </div>

          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium flex items-center">
              <User className="w-4 h-4 mr-2" />
              Full Name
            </Label>
            <Input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="John Doe"
              className="w-full"
            />
          </div>

          {/* Use Case */}
          <div className="space-y-2">
            <Label htmlFor="use_case" className="text-sm font-medium flex items-center">
              <MessageSquare className="w-4 h-4 mr-2" />
              How will you use EmailAI?
            </Label>
            <Textarea
              id="use_case"
              value={formData.use_case}
              onChange={(e) => handleInputChange('use_case', e.target.value)}
              placeholder="Managing team emails, automating responses, organizing client communications..."
              className="w-full min-h-[80px] resize-none"
              maxLength={500}
            />
            <p className="text-xs text-gray-500">
              {formData.use_case?.length || 0}/500 characters
            </p>
          </div>

          {/* Referral Source */}
          <div className="space-y-2">
            <Label htmlFor="referral_source" className="text-sm font-medium flex items-center">
              <Users className="w-4 h-4 mr-2" />
              How did you hear about us?
            </Label>
            <Input
              id="referral_source"
              type="text"
              value={formData.referral_source}
              onChange={(e) => handleInputChange('referral_source', e.target.value)}
              placeholder="Twitter, Product Hunt, Friend, Google..."
              className="w-full"
            />
          </div>

          {/* Priority Score Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Star className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-800">Boost Your Priority</h4>
                <p className="text-sm text-blue-700 mt-1">
                  Providing more details increases your priority score and gets you earlier access!
                </p>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={loading || !formData.email}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Joining Waitlist...
              </>
            ) : (
              <>
                <Mail className="w-5 h-5 mr-2" />
                Join the Waitlist
              </>
            )}
          </Button>

        </form>
      </CardContent>
    </Card>
  );
}