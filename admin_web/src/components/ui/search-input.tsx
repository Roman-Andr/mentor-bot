import { type InputHTMLAttributes } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  value: string;
  onChange: (value: string) => void;
}

export function SearchInput({
  value,
  onChange,
  placeholder,
  className,
  ...props
}: SearchInputProps) {
  const t = useTranslations();
  const placeholderText = placeholder ?? t("common.searchPlaceholder");

  return (
    <div className={`relative min-w-64 flex-1 ${className || ""}`}>
      <Search className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
      <Input
        placeholder={placeholderText}
        className="pl-10"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...props}
      />
    </div>
  );
}
