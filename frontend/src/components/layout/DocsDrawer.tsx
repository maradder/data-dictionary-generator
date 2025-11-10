import { BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { DocsContent } from './DocsContent';

export function DocsDrawer() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="gap-2"
          aria-label="Open documentation"
        >
          <BookOpen className="h-4 w-4" />
          <span className="hidden sm:inline">Help</span>
        </Button>
      </SheetTrigger>
      <SheetContent
        side="right"
        className="w-full sm:w-[540px] sm:max-w-[540px] overflow-y-auto"
      >
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2 text-xl">
            <BookOpen className="h-5 w-5 text-primary" />
            Documentation
          </SheetTitle>
          <SheetDescription>
            Learn how to use the Data Dictionary Generator
          </SheetDescription>
        </SheetHeader>
        <div className="mt-6">
          <DocsContent />
        </div>
      </SheetContent>
    </Sheet>
  );
}
