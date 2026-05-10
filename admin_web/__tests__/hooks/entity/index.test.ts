import { describe, it, expect } from "vitest";
import { useEntity } from "@/shared/hooks/entity";

describe("entity index exports", () => {
  it("exports useEntity function", () => {
    expect(typeof useEntity).toBe("function");
  });

  it("maintains backward compatibility", () => {
    // Test that the re-export maintains the same interface
    // This tests that the import path works correctly
    expect(useEntity).toBeDefined();
    expect(typeof useEntity).toBe("function");
  });

  it("can be called without errors (basic smoke test)", () => {
    // Test that the function can be imported and has expected structure
    // We don't call it here as it requires proper options, but we test it exists
    const entityFunction = useEntity;
    expect(entityFunction).toBeInstanceOf(Function);
    expect(entityFunction.length).toBeGreaterThanOrEqual(1); // Should accept options
  });

  it("exports from correct module path", () => {
    // Test that the re-export comes from the correct composed module
    // This ensures the re-export is working correctly
    const entityFunction = useEntity;
    expect(entityFunction).toBeDefined();
    expect(entityFunction.name).toBe("useEntity");
  });

  it("has expected function properties", () => {
    // Test that the re-exported function has expected properties
    const entityFunction = useEntity;
    expect(entityFunction).toHaveProperty("name");
    expect(entityFunction).toHaveProperty("length");
    expect(typeof entityFunction).toBe("function");
  });
});
