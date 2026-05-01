import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { TabSwitcher } from "@/components/ui/tab-switcher";
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
    t,
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
        <TabSwitcher tabs={tabs} activeTab={activeTab ?? tabs[0].id} onTabChange={onTabChange} />
        <div className="space-y-4">
          {tabs.map((tab) => (
            <div key={tab.id} className={tab.id === (activeTab ?? tabs[0].id) ? "block" : "hidden"}>
              {tab.content}
            </div>
          ))}
        </div>
        <Dialog open={isCreateOpen || isEditOpen} onOpenChange={onCloseDialog}>
          <DialogContent className={dialogMaxWidth}>
            <DialogHeader>
              <DialogTitle>{mode === "create" ? (createButtonLabel ?? defaultCreateLabel) : (editButtonLabel ?? defaultEditLabel)}</DialogTitle>
            </DialogHeader>
            {renderForm({ formData, onChange: onFormChange, mode })}
            {submitError && (
              <div className="text-destructive mt-2 text-sm">{submitError}</div>
            )}
            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={onCloseDialog}
                className="hover:bg-muted rounded border px-4 py-2"
              >
                {t("cancel") ?? "Cancel"}
              </button>
              <button
                onClick={onSubmit}
                disabled={isSubmitting || !isFormValid}
                className="bg-primary text-primary-foreground hover:bg-primary/90 rounded px-4 py-2 disabled:opacity-50"
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
        t={t}
      />
      <Dialog open={isCreateOpen || isEditOpen} onOpenChange={onCloseDialog}>
        <DialogContent className={dialogMaxWidth}>
          <DialogHeader>
            <DialogTitle>{mode === "create" ? (createButtonLabel ?? defaultCreateLabel) : (editButtonLabel ?? defaultEditLabel)}</DialogTitle>
          </DialogHeader>
          {renderForm({ formData, onChange: onFormChange, mode })}
          {submitError && (
            <div className="text-destructive mt-2 text-sm">{submitError}</div>
          )}
          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={onCloseDialog}
              className="hover:bg-muted rounded border px-4 py-2"
            >
              {t("cancel") ?? "Cancel"}
            </button>
            <button
              onClick={onSubmit}
              disabled={isSubmitting || !isFormValid}
              className="bg-primary text-primary-foreground hover:bg-primary/90 rounded px-4 py-2 disabled:opacity-50"
            >
              {isSubmitting ? t("saving") ?? "Saving..." : (t("save") ?? "Save")}
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
