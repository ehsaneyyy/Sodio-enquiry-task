import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { PlusIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage } from "@/lib/apiClient"
import { useCreateEnquiryMutation } from "@/features/enquiries/hooks/useEnquiries"

export function CreateEnquiryDialog() {
  const [isOpen, setIsOpen] = useState(false)
  const [enquiryText, setEnquiryText] = useState("")
  const createEnquiryMutation = useCreateEnquiryMutation()
  const navigate = useNavigate()

  const canSubmit = enquiryText.trim().length > 0 && !createEnquiryMutation.isPending

  function handleSubmit() {
    createEnquiryMutation.mutate(
      { original_text: enquiryText },
      {
        onSuccess: (createdEnquiry) => {
          setIsOpen(false)
          setEnquiryText("")
          navigate(`/enquiries/${createdEnquiry.id}`)
        },
      },
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusIcon />
          New enquiry
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create an enquiry</DialogTitle>
          <DialogDescription>
            Paste the raw enquiry text. It will be extracted and scored automatically.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="enquiry-text">Enquiry text</Label>
            <Textarea
              id="enquiry-text"
              className="min-h-48"
              placeholder="From: Jane Doe&#10;Email: jane@acme.com&#10;Message:&#10;We need a web app, budget around $10k."
              value={enquiryText}
              onChange={(event) => setEnquiryText(event.target.value)}
            />
          </div>
          {createEnquiryMutation.isError ? (
            <p className="text-destructive text-sm">{apiErrorMessage(createEnquiryMutation.error)}</p>
          ) : null}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!canSubmit}>
            {createEnquiryMutation.isPending ? "Extracting…" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
