import { useRef, useState } from "react"
import { UploadCloud } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { apiErrorMessage } from "@/lib/apiClient"
import { useCreateBatchMutation } from "@/features/batches/hooks/useBatches"

export function BatchUploadCard({ onBatchCreated }: { onBatchCreated: (batchId: number) => void }) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const createBatchMutation = useCreateBatchMutation()

  function handleFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  function handleUpload() {
    if (!selectedFile) {
      return
    }
    createBatchMutation.mutate(selectedFile, {
      onSuccess: (createdBatch) => {
        setSelectedFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
        onBatchCreated(createdBatch.batch_id)
      },
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload a batch</CardTitle>
        <CardDescription>
          Upload a text file of enquiries separated by lines of dashes. Each one is extracted and scored.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.text,.md"
            className="hidden"
            onChange={handleFileSelected}
          />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
            <UploadCloud />
            {selectedFile ? selectedFile.name : "Choose file"}
          </Button>
          <Button onClick={handleUpload} disabled={!selectedFile || createBatchMutation.isPending}>
            {createBatchMutation.isPending ? "Uploading…" : "Process batch"}
          </Button>
        </div>
        {createBatchMutation.isError ? (
          <p className="text-destructive mt-3 text-sm">{apiErrorMessage(createBatchMutation.error)}</p>
        ) : null}
      </CardContent>
    </Card>
  )
}
