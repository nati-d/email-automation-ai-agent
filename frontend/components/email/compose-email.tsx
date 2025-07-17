'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateAndSendEmail } from '@/lib/queries'
import { useEmailStore } from '@/lib/store'
import { useToast } from '@/components/providers/toast-provider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import {
  Send,
  Paperclip,
  X,
  Loader2,
  Minimize2,
  Maximize2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const composeSchema = z.object({
  to: z.string().min(1, 'At least one recipient is required'),
  cc: z.string().optional(),
  bcc: z.string().optional(),
  subject: z.string().min(1, 'Subject is required'),
  body: z.string().min(1, 'Message body is required'),
})

type ComposeFormData = z.infer<typeof composeSchema>

export function ComposeEmail() {
  const { isComposeOpen, closeCompose } = useEmailStore()
  const sendEmail = useCreateAndSendEmail()
  const { toast } = useToast()
  const [isMinimized, setIsMinimized] = useState(false)
  const [attachments, setAttachments] = useState<File[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm<ComposeFormData>({
    resolver: zodResolver(composeSchema),
    defaultValues: {
      to: '',
      cc: '',
      bcc: '',
      subject: '',
      body: '',
    },
  })

  const onSubmit = async (data: ComposeFormData) => {
    try {
      const emailData = {
        to: data.to.split(',').map(email => email.trim()).filter(Boolean),
        cc: data.cc ? data.cc.split(',').map(email => email.trim()).filter(Boolean) : undefined,
        bcc: data.bcc ? data.bcc.split(',').map(email => email.trim()).filter(Boolean) : undefined,
        subject: data.subject,
        body: data.body,
        attachments: attachments.length > 0 ? attachments : undefined,
      }

      await sendEmail.mutateAsync(emailData)
      
      toast.success(
        'Email sent successfully!',
        `Your email "${data.subject}" has been sent to ${emailData.to.join(', ')}`
      )
      
      reset()
      setAttachments([])
      closeCompose()
    } catch (error) {
      console.error('Failed to send email:', error)
      toast.error(
        'Failed to send email',
        error instanceof Error ? error.message : 'An unexpected error occurred'
      )
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const handleClose = () => {
    const hasContent = watch('to') || watch('subject') || watch('body')
    if (hasContent) {
      const shouldClose = confirm('Discard this draft?')
      if (!shouldClose) return
    }
    reset()
    setAttachments([])
    closeCompose()
  }

  if (!isComposeOpen) return null

  return (
    <Dialog open={isComposeOpen} onOpenChange={handleClose}>
      <DialogContent className={cn(
        'max-w-2xl max-h-[80vh] p-0',
        isMinimized && 'h-12 max-h-12 overflow-hidden'
      )}>
        <DialogHeader className="p-4 pb-2 flex-row items-center justify-between space-y-0">
          <DialogTitle className={cn(
            'text-lg font-semibold',
            isMinimized && 'text-sm'
          )}>
            {isMinimized ? 'New Message' : 'Compose Email'}
          </DialogTitle>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? (
                <Maximize2 className="h-3 w-3" />
              ) : (
                <Minimize2 className="h-3 w-3" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={handleClose}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </DialogHeader>

        {!isMinimized && (
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col h-full">
            <div className="px-4 space-y-4">
              {/* Recipients */}
              <div className="space-y-2">
                <Label htmlFor="to">To</Label>
                <Input
                  id="to"
                  placeholder="recipient@example.com, another@example.com"
                  {...register('to')}
                  className={cn(errors.to && 'border-red-500')}
                />
                {errors.to && (
                  <p className="text-sm text-red-500">{errors.to.message}</p>
                )}
              </div>

              {/* CC */}
              <div className="space-y-2">
                <Label htmlFor="cc">CC (optional)</Label>
                <Input
                  id="cc"
                  placeholder="cc@example.com"
                  {...register('cc')}
                />
              </div>

              {/* BCC */}
              <div className="space-y-2">
                <Label htmlFor="bcc">BCC (optional)</Label>
                <Input
                  id="bcc"
                  placeholder="bcc@example.com"
                  {...register('bcc')}
                />
              </div>

              {/* Subject */}
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  placeholder="Email subject"
                  {...register('subject')}
                  className={cn(errors.subject && 'border-red-500')}
                />
                {errors.subject && (
                  <p className="text-sm text-red-500">{errors.subject.message}</p>
                )}
              </div>

              {/* Attachments */}
              {attachments.length > 0 && (
                <div className="space-y-2">
                  <Label>Attachments</Label>
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                      <Badge key={index} variant="secondary" className="gap-1">
                        {file.name}
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-3 w-3 p-0"
                          onClick={() => removeAttachment(index)}
                        >
                          <X className="h-2 w-2" />
                        </Button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Message body */}
            <div className="flex-1 px-4 py-2">
              <Textarea
                placeholder="Write your message..."
                className="min-h-[200px] resize-none border-0 focus-visible:ring-0"
                {...register('body')}
              />
              {errors.body && (
                <p className="text-sm text-red-500 mt-1">{errors.body.message}</p>
              )}
            </div>

            {/* Actions */}
            <div className="p-4 border-t flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="gap-2"
                >
                  {isSubmitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  Send
                </Button>

                <input
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </div>

              <Button
                type="button"
                variant="ghost"
                onClick={handleClose}
              >
                Discard
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}