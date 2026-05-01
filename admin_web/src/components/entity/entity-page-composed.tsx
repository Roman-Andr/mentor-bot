import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EntityPageHeader } from "./entity-page-header";
import { EntityPageTable } from "./entity-page-table";
import type { EntityPageProps } from "./entity-page-types";
import { useTranslations } from "@/hooks/use-translations";

export function EntityPage<TItem, TForm>(props: EntityPageProps<TItem, TForm>) {
  const {
    title,
    description,
    items,
    totalItems,
    currentPage,
    pageSize,
    isLoading,
    isCreateOpen,
    isEditOpen,
    selectedItem,
    onCreateOpen,
    onEditOpen,
    onDelete,
    onCloseDialog,
    formData,
    onFormChange,
    onSubmit,
    isSubmitting,
    submitError,
    searchQuery,
    onSearchChange,
    onPageChange,
    onPageSizeChange,
    columns,
    renderForm,
    createButtonLabel,
    editButtonLabel,
    emptyStateMessage,
    tabs,
    activeTab,
    onTabChange,
    filters,
    additionalActions,
    getItemKey,
    onRowClick,
    showSearch,
    searchPlaceholder,
    isFormValid = true,
    dialogMaxWidth = "max-w-2xl",
    sortField,
    sortDirection,
    onSort,
  } = props;

  const t = useTranslations("common");
  const mode = isEditOpen ? "edit" : "create";

  const defaultCreateLabel = t("create") ?? "Create";
  const defaultEditLabel = t("edit") ?? "Edit";
  const defaultEmptyMessage = t("noItems") ?? "No items found";

  // Tabbed interface
  if (tabs && tabs.length > 0) {
    return (
      <div className="space-y-4">
        <EntityPageHeader
          title={title}
          description={description}
          showSearch={showSearch}
          searchPlaceholder={searchPlaceholder}
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          filters={filters}
          additionalActions={additionalActions}
          createButtonLabel={createButtonLabel ?? defaultCreateLabel}
          onCreateOpen={onCreateOpen}
        />
        <Tabs value={activeTab ?? tabs[0].id} onValueChange={onTabChange}>
          <TabsList>
            {tabs.map((tab) => (
              <TabsTrigger key={tab.id} value={tab.id}>
                {tab.icon && <tab.icon className="mr-2 size-4" />}
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>
          {tabs.map((tab) => (
            <TabsContent key={tab.id} value={tab.id}>
              {tab.content}
            </TabsContent>
          ))}
        </Tabs>
        <Dialog open={isCreateOpen || isEditOpen} onOpenChange={onCloseDialog}>
          <DialogContent className={dialogMaxWidth}>
            <DialogHeader>
              <DialogTitle>{mode === "create" ? (createButtonLabel ?? defaultCreateLabel) : (editButtonLabel ?? defaultEditLabel)}</DialogTitle>
            </DialogHeader>
            {renderForm({ formData, onChange: onFormChange, mode })}
            {submitError && (
              <div className="text-sm text-destructive mt-2">{submitError}</div>
            )}
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={onCloseDialog}
                className="px-4 py-2 border rounded hover:bg-muted"
              >
                {t("cancel") ?? "Cancel"}
              </button>
              <button
                onClick={onSubmit}
                disabled={isSubmitting || !isFormValid}
                className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
              >
                {isSubmitting ? t("saving") ?? "Saving..." : (t("save") ?? "Save")}
              </button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // Standard table view
  return (
    <div className="space-y-4">
      <EntityPageHeader
        title={title}
        description={description}
        showSearch={showSearch}
        searchPlaceholder={searchPlaceholder}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        filters={filters}
        additionalActions={additionalActions}
        createButtonLabel={createButtonLabel ?? defaultCreateLabel}
        onCreateOpen={onCreateOpen}
      />
      <EntityPageTable
        items={items}
        totalItems={totalItems}
        currentPage={currentPage}
        pageSize={pageSize}
        isLoading={isLoading}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
        columns={columns}
        getItemKey={getItemKey}
        onRowClick={onRowClick}
        onEditOpen={onEditOpen}
        onDelete={onDelete}
        title={title}
        description={description}
        showSearch={showSearch}
        searchPlaceholder={searchPlaceholder}
        filters={filters}
        additionalActions={additionalActions}
        createButtonLabel={createButtonLabel ?? defaultCreateLabel}
        onCreateOpen={onCreateOpen}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={onSort}
        emptyStateMessage={emptyStateMessage ?? defaultEmptyMessage}
      />
      <Dialog open={isCreateOpen || isEditOpen} onOpenChange={onCloseDialog}>
        <DialogContent className={dialogMaxWidth}>
          <DialogHeader>
            <DialogTitle>{mode === "create" ? (createButtonLabel ?? defaultCreateLabel) : (editButtonLabel ?? defaultEditLabel)}</DialogTitle>
          </DialogHeader>
          {renderForm({ formData, onChange: onFormChange, mode })}
          {submitError && (
            <div className="text-sm text-destructive mt-2">{submitError}</div>
          )}
          <div className="flex justify-end gap-2 mt-4">
            <button
              onClick={onCloseDialog}
              className="px-4 py-2 border rounded hover:bg-muted"
            >
              {t("cancel") ?? "Cancel"}
            </button>
            <button
              onClick={onSubmit}
              disabled={isSubmitting || !isFormValid}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
            >
              {isSubmitting ? t("saving") ?? "Saving..." : (t("save") ?? "Save")}
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
