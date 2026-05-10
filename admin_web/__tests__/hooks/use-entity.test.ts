import { describe, it, expect } from "vitest";
import { useEntity } from "@/shared/hooks/use-entity";
import { useEntity as useEntityFromDirectory } from "@/shared/hooks/entity";

describe("use-entity exports", () => {
  it("exports useEntity function", () => {
    expect(typeof useEntity).toBe("function");
    expect(useEntityFromDirectory).toBe(useEntity);
  });
});
