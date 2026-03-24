import { type InputHTMLAttributes } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  value: string;
  onChange: (value: string) => void;
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Поиск...",
  className,
  ...props
}: SearchInputProps) {
  return (
    <div className="relative w-64">
      <Search className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
      <Input
        placeholder={placeholder}
        className={`pl-10 ${className || ""}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...props}
      />
    </div>
  );
}
