"""Unit tests for telegram_bot/keyboards/knowledge_kb.py."""


from telegram_bot.keyboards.knowledge_kb import (
    get_admin_knowledge_keyboard,
    get_article_view_keyboard,
    get_faq_keyboard,
    get_faq_scenario_keyboard,
    get_kb_article_saved_keyboard,
    get_kb_categories_keyboard,
    get_kb_category_article_view_keyboard,
    get_kb_category_articles_keyboard,
    get_kb_create_files_keyboard,
    get_kb_upload_complete_keyboard,
    get_kb_upload_files_keyboard,
    get_knowledge_base_menu_keyboard,
    get_search_no_results_keyboard,
    get_search_results_keyboard,
)


class TestKnowledgeBaseKeyboards:
    """Test cases for knowledge base keyboards."""

    def test_get_knowledge_base_menu_keyboard(self):
        """Test knowledge base main menu keyboard."""
        builder = get_knowledge_base_menu_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_knowledge_base_menu_keyboard_russian(self):
        """Test knowledge base main menu keyboard - Russian locale."""
        builder = get_knowledge_base_menu_keyboard(locale="ru")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_search_no_results_keyboard(self):
        """Test search no results keyboard."""
        builder = get_search_no_results_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_search_results_keyboard_basic(self):
        """Test search results keyboard with basic results."""
        # Create mock result objects with title attribute
        class MockResult:
            def __init__(self, title):
                self.title = title

        results = [MockResult("Result 1"), MockResult("Result 2")]
        builder = get_search_results_keyboard(results, locale="en", page=1, total_pages=1, query="test")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_search_results_keyboard_with_pagination(self):
        """Test search results keyboard with pagination."""
        class MockResult:
            def __init__(self, title):
                self.title = title

        results = [MockResult(f"Result {i}") for i in range(5)]
        builder = get_search_results_keyboard(
            results, locale="en", page=2, total_pages=3, query="test"
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_search_results_keyboard_first_page(self):
        """Test search results keyboard on first page."""
        class MockResult:
            def __init__(self, title):
                self.title = title

        results = [MockResult("Result 1")]
        builder = get_search_results_keyboard(
            results, locale="en", page=1, total_pages=2, query="test"
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_search_results_keyboard_last_page(self):
        """Test search results keyboard on last page."""
        class MockResult:
            def __init__(self, title):
                self.title = title

        results = [MockResult("Result 1")]
        builder = get_search_results_keyboard(
            results, locale="en", page=2, total_pages=2, query="test"
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_article_view_keyboard_without_attachments(self):
        """Test article view keyboard without attachments."""
        builder = get_article_view_keyboard([], 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_article_view_keyboard_with_attachments(self):
        """Test article view keyboard with attachments."""
        attachments = [
            {"id": 1, "name": "file1.pdf"},
            {"id": 2, "name": "file2.doc"},
        ]
        builder = get_article_view_keyboard(attachments, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_article_view_keyboard_from_search(self):
        """Test article view keyboard from search results."""
        builder = get_article_view_keyboard([], 1, locale="en", from_search=True, search_page=2)
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_categories_keyboard_with_categories(self):
        """Test categories keyboard with categories."""
        categories = [
            {"id": 1, "name": "Category 1", "articles_count": 5},
            {"id": 2, "name": "Category 2", "articles_count": 0},
        ]
        builder = get_kb_categories_keyboard(categories, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_categories_keyboard_without_categories(self):
        """Test categories keyboard without categories."""
        builder = get_kb_categories_keyboard(None, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_categories_keyboard_empty_list(self):
        """Test categories keyboard with empty list."""
        builder = get_kb_categories_keyboard([], locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_categories_keyboard_many_categories(self):
        """Test categories keyboard with many categories (should limit to 20)."""
        categories = [{"id": i, "name": f"Category {i}", "articles_count": i} for i in range(25)]
        builder = get_kb_categories_keyboard(categories, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_articles_keyboard_basic(self):
        """Test category articles keyboard."""
        articles = [
            {"id": 1, "title": "Article 1"},
            {"id": 2, "title": "Article 2"},
        ]
        builder = get_kb_category_articles_keyboard(articles, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_articles_keyboard_with_pagination(self):
        """Test category articles keyboard with pagination."""
        articles = [{"id": i, "title": f"Article {i}"} for i in range(5)]
        builder = get_kb_category_articles_keyboard(
            articles, 1, locale="en", page=2, total_pages=3
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_articles_keyboard_first_page(self):
        """Test category articles keyboard on first page."""
        articles = [{"id": 1, "title": "Article 1"}]
        builder = get_kb_category_articles_keyboard(
            articles, 1, locale="en", page=1, total_pages=2
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_articles_keyboard_last_page(self):
        """Test category articles keyboard on last page."""
        articles = [{"id": 1, "title": "Article 1"}]
        builder = get_kb_category_articles_keyboard(
            articles, 1, locale="en", page=2, total_pages=2
        )
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_article_view_keyboard_without_attachments(self):
        """Test category article view keyboard without attachments."""
        builder = get_kb_category_article_view_keyboard([], 1, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_article_view_keyboard_with_attachments(self):
        """Test category article view keyboard with attachments."""
        attachments = [
            {"id": 1, "name": "file1.pdf"},
            {"id": 2, "name": "file2.doc"},
        ]
        builder = get_kb_category_article_view_keyboard(attachments, 1, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_category_article_view_keyboard_with_page(self):
        """Test category article view keyboard with page."""
        attachments = [{"id": 1, "name": "file1.pdf"}]
        builder = get_kb_category_article_view_keyboard(attachments, 1, 1, locale="en", page=2)
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_keyboard_with_scenarios(self):
        """Test FAQ keyboard with scenarios."""
        scenarios = [
            {"id": 1, "title": "Scenario 1", "category": "General"},
            {"id": 2, "title": "Scenario 2", "category": ""},
        ]
        builder = get_faq_keyboard(scenarios, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_keyboard_without_scenarios(self):
        """Test FAQ keyboard without scenarios."""
        builder = get_faq_keyboard(None, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_keyboard_empty_list(self):
        """Test FAQ keyboard with empty list."""
        builder = get_faq_keyboard([], locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_keyboard_many_scenarios(self):
        """Test FAQ keyboard with many scenarios (should limit to 15)."""
        scenarios = [{"id": i, "title": f"Scenario {i}", "category": "General"} for i in range(20)]
        builder = get_faq_keyboard(scenarios, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_scenario_keyboard_with_steps(self):
        """Test FAQ scenario keyboard with steps."""
        steps = [
            {"id": 1, "content": "Step 1", "options": [{"label": "Option 1", "next_step": 2}]},
        ]
        builder = get_faq_scenario_keyboard(1, steps, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_scenario_keyboard_with_multiple_options(self):
        """Test FAQ scenario keyboard with multiple options."""
        steps = [
            {
                "id": 1,
                "content": "Step 1",
                "options": [
                    {"label": "Option 1", "next_step": 2},
                    {"label": "Option 2", "next_step": 3},
                ],
            },
        ]
        builder = get_faq_scenario_keyboard(1, steps, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_faq_scenario_keyboard_step_not_found(self):
        """Test FAQ scenario keyboard when step not found."""
        steps = [{"id": 2, "content": "Step 2"}]  # Step ID doesn't match current_step_id
        builder = get_faq_scenario_keyboard(1, steps, 1, locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_admin_knowledge_keyboard(self):
        """Test admin knowledge base keyboard."""
        builder = get_admin_knowledge_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_create_files_keyboard(self):
        """Test article creation files keyboard."""
        builder = get_kb_create_files_keyboard()
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_article_saved_keyboard(self):
        """Test article saved keyboard."""
        builder = get_kb_article_saved_keyboard(locale="en")
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_upload_files_keyboard(self):
        """Test upload files keyboard."""
        builder = get_kb_upload_files_keyboard()
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")

    def test_get_kb_upload_complete_keyboard(self):
        """Test upload complete keyboard."""
        builder = get_kb_upload_complete_keyboard()
        markup = builder.as_markup()

        assert markup is not None
        assert hasattr(markup, "inline_keyboard")
