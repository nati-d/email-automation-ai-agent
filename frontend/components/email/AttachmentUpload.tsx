import React from "react";

interface AttachmentUploadProps {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
  maxTotalBytes?: number;
}

const bytesToReadable = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const AttachmentUpload: React.FC<AttachmentUploadProps> = ({
  files,
  onChange,
  disabled,
  maxTotalBytes = 20 * 1024 * 1024,
}) => {
  const inputRef = React.useRef<HTMLInputElement | null>(null);

  const handlePick = () => {
    inputRef.current?.click();
  };

  const handleFiles = (event: React.ChangeEvent<HTMLInputElement>) => {
    const list = event.target.files;
    if (!list) return;
    const newFiles = Array.from(list);
    const merged = [...files, ...newFiles];
    onChange(merged);
    event.target.value = ""; // reset
  };

  const removeAt = (idx: number) => {
    const next = files.filter((_, i) => i !== idx);
    onChange(next);
  };

  const totalBytes = files.reduce((sum, f) => sum + f.size, 0);
  const overLimit = totalBytes > maxTotalBytes;

  return (
    <div className="border rounded-lg p-3 bg-muted/20">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium">Attachments</div>
        <button
          type="button"
          className="text-sm px-2 py-1 border rounded disabled:opacity-50"
          onClick={handlePick}
          disabled={disabled}
        >
          + Add files
        </button>
      </div>
      <input
        ref={inputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFiles}
      />
      {files.length === 0 ? (
        <div className="text-xs text-muted-foreground">No files attached.</div>
      ) : (
        <ul className="space-y-2">
          {files.map((f, idx) => (
            <li
              key={`${f.name}-${idx}`}
              className="flex items-center justify-between text-sm"
            >
              <div className="truncate mr-2">
                <span className="font-medium">{f.name}</span>
                <span className="ml-2 text-muted-foreground">
                  {bytesToReadable(f.size)}
                </span>
              </div>
              <button
                type="button"
                className="text-xs px-2 py-1 border rounded"
                onClick={() => removeAt(idx)}
                disabled={disabled}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <div
        className={`mt-2 text-xs ${
          overLimit ? "text-red-600" : "text-muted-foreground"
        }`}
      >
        Total: {bytesToReadable(totalBytes)} / {bytesToReadable(maxTotalBytes)}
        {overLimit && " (over Gmail limit, please remove some files)"}
      </div>
    </div>
  );
};

export default AttachmentUpload;
