import { Info } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { ReactNode } from 'react';

interface InfoModalProps {
  title: string;
  children: ReactNode;
  triggerClassName?: string;
  triggerIcon?: ReactNode;
  triggerLabel?: string;
}

export function InfoModal({
  title,
  children,
  triggerClassName = '',
  triggerIcon,
  triggerLabel,
}: InfoModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        {triggerLabel ? (
          <Button
            variant="ghost"
            size="sm"
            className={`gap-2 ${triggerClassName}`}
          >
            {triggerIcon || <Info className="h-4 w-4" />}
            {triggerLabel}
          </Button>
        ) : (
          <button
            className={`inline-flex items-center justify-center rounded-full p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors ${triggerClassName}`}
            aria-label={`More information about ${title}`}
          >
            {triggerIcon || <Info className="h-4 w-4" />}
          </button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-primary" />
            {title}
          </DialogTitle>
          <DialogDescription className="sr-only">
            Help information about {title}
          </DialogDescription>
        </DialogHeader>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
}
