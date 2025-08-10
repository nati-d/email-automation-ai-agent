"""
Category Use Cases

Business use cases for category operations.
"""

from typing import List

from ...domain.entities.category import Category
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.repositories.email_repository import EmailRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email_address import EmailAddress

from ..dto.category_dto import CategoryDTO, CreateCategoryDTO, UpdateCategoryDTO, CategoryListDTO


class CategoryUseCaseBase:
    """Base class for category use cases"""
    
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
    
    def _entity_to_dto(self, category: Category) -> CategoryDTO:
        """Convert category entity to DTO"""
        return CategoryDTO(
            id=category.id,
            user_id=category.user_id,
            name=category.name,
            description=category.description,
            color=category.color,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    def _dto_to_entity(self, dto: CreateCategoryDTO) -> Category:
        """Convert create DTO to category entity"""
        return Category.create(
            user_id=dto.user_id,
            name=dto.name,
            description=dto.description,
            color=dto.color
        )


class CreateCategoryUseCase(CategoryUseCaseBase):
    """Use case for creating categories"""
    
    def __init__(self, category_repository: CategoryRepository, email_repository: EmailRepository = None, user_repository: UserRepository = None):
        super().__init__(category_repository)
        self.email_repository = email_repository
        self.user_repository = user_repository
    
    async def execute(self, dto: CreateCategoryDTO) -> CategoryDTO:
        """Create a new category"""
        print(f"🔧 DEBUG: [CreateCategoryUseCase] execute called")
        print(f"🔧 DEBUG: [CreateCategoryUseCase] dto: {dto}")
        
        try:
            # Check if category with same name already exists for this user
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Checking for existing category with name: {dto.name}")
            existing_category = await self.category_repository.find_by_name_and_user(dto.name, dto.user_id)
            
            if existing_category:
                print(f"🔧 DEBUG: [CreateCategoryUseCase] Category already exists: {existing_category}")
                raise DomainValidationError(f"Category '{dto.name}' already exists for this user")
            else:
                print(f"🔧 DEBUG: [CreateCategoryUseCase] No existing category found, creating new one")
            
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Creating category entity")
            category = self._dto_to_entity(dto)
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Category entity created: {category}")
            
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Saving category to repository")
            saved_category = await self.category_repository.save(category)
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Category saved: {saved_category}")
            
            # Re-categorize emails with the new category
            if self.email_repository:
                print(f"🔧 DEBUG: [CreateCategoryUseCase] Re-categorizing emails with new category")
                await self._recategorize_emails_with_new_category(dto.user_id, saved_category.name)
            
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Converting to DTO")
            result_dto = self._entity_to_dto(saved_category)
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Returning DTO: {result_dto}")
            
            return result_dto
            
        except Exception as e:
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Error in execute: {e}")
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Full traceback: {traceback.format_exc()}")
            raise
    
    async def _recategorize_emails_with_new_category(self, user_id: str, new_category_name: str) -> None:
        """Re-categorize emails that might match the new category"""
        print(f"🔧 DEBUG: [CreateCategoryUseCase] _recategorize_emails_with_new_category called")
        print(f"🔧 DEBUG: [CreateCategoryUseCase] user_id: {user_id}, new_category: {new_category_name}")
        
        try:
            if not self.user_repository:
                print(f"🔧 DEBUG: [CreateCategoryUseCase] No user repository available, skipping re-categorization")
                return
            
            # Get user's email address first
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                print(f"🔧 DEBUG: [CreateCategoryUseCase] User not found: {user_id}")
                return
            
            user_email = str(user.email)
            print(f"🔧 DEBUG: [CreateCategoryUseCase] User email: {user_email}")
            
            # Get all inbox emails for the user by email address
            emails = await self.email_repository.find_by_recipient(EmailAddress.create(user_email), limit=1000)
            inbox_emails = [email for email in emails if email.email_type.value == "inbox"]
            
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Found {len(inbox_emails)} inbox emails to check")
            
            recategorized_count = 0
            for email in inbox_emails:
                # Check if email content matches the new category
                if self._email_matches_category(email, new_category_name):
                    print(f"🔧 DEBUG: [CreateCategoryUseCase] Email {email.id} matches new category '{new_category_name}'")
                    email.update_category(new_category_name)
                    await self.email_repository.update(email)
                    recategorized_count += 1
            
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Re-categorized {recategorized_count} emails with new category '{new_category_name}'")
            
        except Exception as e:
            print(f"🔧 DEBUG: [CreateCategoryUseCase] Error in _recategorize_emails_with_new_category: {e}")
            # Don't fail the category creation if re-categorization fails
            pass
    
    def _email_matches_category(self, email, category_name: str) -> bool:
        """Check if email content matches a specific category with enhanced precision"""
        # Combine subject and body for analysis
        text_to_analyze = f"{email.subject} {email.body}".lower()
        category_name_lower = category_name.lower()
        
        # Enhanced keywords with weights and context
        category_keywords = {
            "work": {
                "high_weight": ["meeting", "deadline", "project", "presentation", "report", "client", "business"],
                "medium_weight": ["work", "office", "team", "collaboration", "agenda", "minutes", "proposal"],
                "low_weight": ["schedule", "update", "review", "discussion", "planning"]
            },
            "amazon": {
                "high_weight": ["amazon", "order", "shipping", "delivery", "tracking", "package"],
                "medium_weight": ["purchase", "product", "item", "shipment", "arrival"],
                "low_weight": ["buy", "bought", "received", "arrived"]
            },
            "mastercard": {
                "high_weight": ["mastercard", "credit card", "payment", "transaction", "charge"],
                "medium_weight": ["statement", "account", "balance", "billing"],
                "low_weight": ["bank", "financial", "money"]
            },
            "personal": {
                "high_weight": ["family", "friend", "birthday", "anniversary", "love", "party"],
                "medium_weight": ["personal", "home", "dinner", "lunch", "coffee"],
                "low_weight": ["meet", "catch up", "visit"]
            },
            "finance": {
                "high_weight": ["bank", "account", "balance", "transfer", "investment", "loan"],
                "medium_weight": ["financial", "money", "budget", "expense", "income"],
                "low_weight": ["payment", "transaction", "statement"]
            },
            "shopping": {
                "high_weight": ["purchase", "buy", "sale", "discount", "coupon", "deal"],
                "medium_weight": ["store", "shop", "retail", "offer", "promotion"],
                "low_weight": ["product", "item", "price", "cost"]
            },
            "codeforces": {
                "high_weight": ["codeforces", "contest", "problem", "submission", "rating", "div"],
                "medium_weight": ["algorithm", "programming", "coding", "solution", "test"],
                "low_weight": ["code", "program", "challenge", "competition"]
            },
            "uncategorized": {
                "high_weight": ["uncategorized", "unknown", "misc", "other"],
                "medium_weight": [],
                "low_weight": []
            }
        }
        
        # Calculate weighted score
        total_score = 0
        
        # Check for direct category name match (high weight)
        if category_name_lower in text_to_analyze:
            total_score += 10
        
        # Check for category-specific keywords
        if category_name_lower in category_keywords:
            keywords = category_keywords[category_name_lower]
            
            # High weight keywords (3 points each)
            for keyword in keywords["high_weight"]:
                if keyword in text_to_analyze:
                    total_score += 3
            
            # Medium weight keywords (2 points each)
            for keyword in keywords["medium_weight"]:
                if keyword in text_to_analyze:
                    total_score += 2
            
            # Low weight keywords (1 point each)
            for keyword in keywords["low_weight"]:
                if keyword in text_to_analyze:
                    total_score += 1
        
        # Additional context-based scoring
        total_score += self._calculate_context_score(email, category_name_lower)
        
        # Threshold for matching (higher threshold = more precise)
        threshold = 5 if category_name_lower in ["work", "finance", "personal"] else 3
        
        print(f"🔧 DEBUG: [CreateCategoryUseCase] Email {email.id} category '{category_name}' score: {total_score} (threshold: {threshold})")
        
        return total_score >= threshold
    
    def _calculate_context_score(self, email, category_name: str) -> int:
        """Calculate additional context-based score for more precise categorization"""
        score = 0
        text_to_analyze = f"{email.subject} {email.body}".lower()
        
        # Sender-based scoring
        sender_email = str(email.sender).lower()
        
        # Domain-based scoring
        if category_name == "work":
            work_domains = ["company.com", "corp.com", "business.com", "office.com"]
            if any(domain in sender_email for domain in work_domains):
                score += 2
        
        elif category_name == "amazon":
            if "amazon" in sender_email or "amzn" in sender_email:
                score += 3
        
        elif category_name == "mastercard":
            if "mastercard" in sender_email or "bank" in sender_email:
                score += 3
        
        elif category_name == "codeforces":
            if "codeforces" in sender_email:
                score += 3
        
        # Subject line analysis
        subject_lower = email.subject.lower()
        
        # Time-based context (work emails during work hours)
        if category_name == "work":
            work_indicators = ["meeting", "agenda", "minutes", "report", "deadline"]
            if any(indicator in subject_lower for indicator in work_indicators):
                score += 2
        
        # Urgency indicators
        urgency_words = ["urgent", "asap", "immediate", "critical", "important"]
        if any(word in text_to_analyze for word in urgency_words):
            if category_name == "work":
                score += 1
        
        # Length-based scoring (longer emails might be more important)
        if len(email.body) > 500 and category_name == "work":
            score += 1
        
        return score


class GetCategoryUseCase(CategoryUseCaseBase):
    """Use case for getting categories"""
    
    async def execute(self, category_id: str) -> CategoryDTO:
        """Get a category by ID"""
        category = await self.category_repository.find_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)
        
        return self._entity_to_dto(category)


class UpdateCategoryUseCase(CategoryUseCaseBase):
    """Use case for updating categories"""
    
    async def execute(self, category_id: str, dto: UpdateCategoryDTO) -> CategoryDTO:
        """Update category information"""
        category = await self.category_repository.find_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)
        
        # Check if new name conflicts with existing category
        if dto.name and dto.name != category.name:
            existing_category = await self.category_repository.find_by_name_and_user(dto.name, category.user_id)
            if existing_category:
                raise DomainValidationError(f"Category '{dto.name}' already exists for this user")
        
        # Update category properties
        if dto.name is not None:
            category.update_name(dto.name)
        
        if dto.description is not None:
            category.update_description(dto.description)
        
        if dto.color is not None:
            category.update_color(dto.color)
        
        if dto.is_active is not None:
            if dto.is_active:
                category.activate()
            else:
                category.deactivate()
        
        updated_category = await self.category_repository.update(category)
        return self._entity_to_dto(updated_category)


class DeleteCategoryUseCase(CategoryUseCaseBase):
    """Use case for deleting categories"""
    
    def __init__(self, category_repository: CategoryRepository, email_repository: EmailRepository):
        super().__init__(category_repository)
        self.email_repository = email_repository
    
    async def execute(self, category_id: str) -> bool:
        """Delete a category"""
        print(f"🔧 DEBUG: [DeleteCategoryUseCase] execute called for category_id: {category_id}")
        
        try:
            category = await self.category_repository.find_by_id(category_id)
            if not category:
                raise EntityNotFoundError("Category", category_id)
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Found category: {category.name}")
            
            # Get the category name before deletion for re-categorization
            category_name = category.name
            user_id = category.user_id
            
            # Delete the category
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Deleting category")
            await self.category_repository.delete(category_id)
            
            # Re-categorize emails that were using this category
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Re-categorizing emails after category deletion")
            recategorized_count = await self._recategorize_emails_after_category_deletion(user_id, category_name)
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Successfully deleted category and re-categorized {recategorized_count} emails")
            return True
            
        except Exception as e:
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Error in execute: {e}")
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Full traceback: {traceback.format_exc()}")
            raise
    
    async def _recategorize_emails_after_category_deletion(self, user_id: str, deleted_category_name: str) -> int:
        """Re-categorize emails after a category is deleted"""
        print(f"🔧 DEBUG: [DeleteCategoryUseCase] _recategorize_emails_after_category_deletion called")
        print(f"🔧 DEBUG: [DeleteCategoryUseCase] user_id: {user_id}, deleted_category: {deleted_category_name}")
        
        try:
            # Get all emails for the user that were using the deleted category
            emails = await self.email_repository.find_by_user_id(user_id)
            affected_emails = [
                email for email in emails 
                if email.email_type.value == "inbox" and email.category == deleted_category_name
            ]
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Found {len(affected_emails)} emails using deleted category")
            
            # Get remaining active categories for re-categorization
            remaining_categories = await self.category_repository.find_active_by_user_id(user_id)
            category_names = [cat.name.lower() for cat in remaining_categories]
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Remaining categories: {category_names}")
            
            recategorized_count = 0
            for email in affected_emails:
                # Find the best matching category from remaining categories
                new_category = self._find_best_matching_category(email, category_names)
                
                print(f"🔧 DEBUG: [DeleteCategoryUseCase] Email {email.id}: {deleted_category_name} -> {new_category}")
                
                # Update the email category
                email.update_category(new_category)
                await self.email_repository.update(email)
                recategorized_count += 1
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Re-categorized {recategorized_count} emails")
            return recategorized_count
            
        except Exception as e:
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Error in _recategorize_emails_after_category_deletion: {e}")
            # Don't fail the category deletion if re-categorization fails
            return 0
    
    def _find_best_matching_category(self, email, available_categories: List[str]) -> str:
        """Find the best matching category for an email from available categories with enhanced precision"""
        # Combine subject and body for analysis
        text_to_analyze = f"{email.subject} {email.body}".lower()
        
        # Enhanced keywords with weights and context
        category_keywords = {
            "work": {
                "high_weight": ["meeting", "deadline", "project", "presentation", "report", "client", "business"],
                "medium_weight": ["work", "office", "team", "collaboration", "agenda", "minutes", "proposal"],
                "low_weight": ["schedule", "update", "review", "discussion", "planning"]
            },
            "amazon": {
                "high_weight": ["amazon", "order", "shipping", "delivery", "tracking", "package"],
                "medium_weight": ["purchase", "product", "item", "shipment", "arrival"],
                "low_weight": ["buy", "bought", "received", "arrived"]
            },
            "mastercard": {
                "high_weight": ["mastercard", "credit card", "payment", "transaction", "charge"],
                "medium_weight": ["statement", "account", "balance", "billing"],
                "low_weight": ["bank", "financial", "money"]
            },
            "personal": {
                "high_weight": ["family", "friend", "birthday", "anniversary", "love", "party"],
                "medium_weight": ["personal", "home", "dinner", "lunch", "coffee"],
                "low_weight": ["meet", "catch up", "visit"]
            },
            "finance": {
                "high_weight": ["bank", "account", "balance", "transfer", "investment", "loan"],
                "medium_weight": ["financial", "money", "budget", "expense", "income"],
                "low_weight": ["payment", "transaction", "statement"]
            },
            "shopping": {
                "high_weight": ["purchase", "buy", "sale", "discount", "coupon", "deal"],
                "medium_weight": ["store", "shop", "retail", "offer", "promotion"],
                "low_weight": ["product", "item", "price", "cost"]
            },
            "codeforces": {
                "high_weight": ["codeforces", "contest", "problem", "submission", "rating", "div"],
                "medium_weight": ["algorithm", "programming", "coding", "solution", "test"],
                "low_weight": ["code", "program", "challenge", "competition"]
            },
            "uncategorized": {
                "high_weight": ["uncategorized", "unknown", "misc", "other"],
                "medium_weight": [],
                "low_weight": []
            }
        }
        
        # Find the best matching category
        best_match = None
        best_score = 0
        
        for category_name in available_categories:
            total_score = 0
            
            # Check for direct category name match (high weight)
            if category_name in text_to_analyze:
                total_score += 10
            
            # Check for category-specific keywords
            if category_name in category_keywords:
                keywords = category_keywords[category_name]
                
                # High weight keywords (3 points each)
                for keyword in keywords["high_weight"]:
                    if keyword in text_to_analyze:
                        total_score += 3
                
                # Medium weight keywords (2 points each)
                for keyword in keywords["medium_weight"]:
                    if keyword in text_to_analyze:
                        total_score += 2
                
                # Low weight keywords (1 point each)
                for keyword in keywords["low_weight"]:
                    if keyword in text_to_analyze:
                        total_score += 1
            
            # Additional context-based scoring
            total_score += self._calculate_context_score(email, category_name)
            
            print(f"🔧 DEBUG: [DeleteCategoryUseCase] Email {email.id} category '{category_name}' score: {total_score}")
            
            if total_score > best_score:
                best_score = total_score
                best_match = category_name
        
        # Return the best match or 'uncategorized' as fallback
        return best_match if best_match else "uncategorized"
    
    def _calculate_context_score(self, email, category_name: str) -> int:
        """Calculate additional context-based score for more precise categorization"""
        score = 0
        text_to_analyze = f"{email.subject} {email.body}".lower()
        
        # Sender-based scoring
        sender_email = str(email.sender).lower()
        
        # Domain-based scoring
        if category_name == "work":
            work_domains = ["company.com", "corp.com", "business.com", "office.com"]
            if any(domain in sender_email for domain in work_domains):
                score += 2
        
        elif category_name == "amazon":
            if "amazon" in sender_email or "amzn" in sender_email:
                score += 3
        
        elif category_name == "mastercard":
            if "mastercard" in sender_email or "bank" in sender_email:
                score += 3
        
        elif category_name == "codeforces":
            if "codeforces" in sender_email:
                score += 3
        
        # Subject line analysis
        subject_lower = email.subject.lower()
        
        # Time-based context (work emails during work hours)
        if category_name == "work":
            work_indicators = ["meeting", "agenda", "minutes", "report", "deadline"]
            if any(indicator in subject_lower for indicator in work_indicators):
                score += 2
        
        # Urgency indicators
        urgency_words = ["urgent", "asap", "immediate", "critical", "important"]
        if any(word in text_to_analyze for word in urgency_words):
            if category_name == "work":
                score += 1
        
        # Length-based scoring (longer emails might be more important)
        if len(email.body) > 500 and category_name == "work":
            score += 1
        
        return score


class ListCategoriesUseCase(CategoryUseCaseBase):
    """Use case for listing categories"""
    
    async def execute(self, user_id: str, include_inactive: bool = False) -> CategoryListDTO:
        """List categories for a user"""
        print(f"🔧 DEBUG: [ListCategoriesUseCase] execute called")
        print(f"🔧 DEBUG: [ListCategoriesUseCase] user_id: {user_id}")
        print(f"🔧 DEBUG: [ListCategoriesUseCase] include_inactive: {include_inactive}")
        
        try:
            if include_inactive:
                print(f"🔧 DEBUG: [ListCategoriesUseCase] Calling find_by_user_id")
                categories = await self.category_repository.find_by_user_id(user_id)
            else:
                print(f"🔧 DEBUG: [ListCategoriesUseCase] Calling find_active_by_user_id")
                categories = await self.category_repository.find_active_by_user_id(user_id)
            
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Repository returned {len(categories)} categories")
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Categories: {categories}")
            
            category_dtos = [self._entity_to_dto(category) for category in categories]
            total_count = len(category_dtos)
            
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Created {total_count} DTOs")
            
            result = CategoryListDTO(
                categories=category_dtos,
                total_count=total_count
            )
            
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Returning result: {result}")
            return result
            
        except Exception as e:
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Error in execute: {e}")
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [ListCategoriesUseCase] Full traceback: {traceback.format_exc()}")
            raise


class RecategorizeEmailsUseCase:
    """Use case for re-categorizing emails when categories change"""
    
    def __init__(self, email_repository: EmailRepository, category_repository: CategoryRepository, user_repository: UserRepository, llm_service=None):
        self.email_repository = email_repository
        self.category_repository = category_repository
        self.user_repository = user_repository
        self.llm_service = llm_service
    
    async def execute(self, user_id: str) -> int:
        """Re-categorize all inbox emails for a user"""
        print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] execute called for user_id: {user_id}")
        
        try:
            # Get user's email address first
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] User not found: {user_id}")
                raise EntityNotFoundError("User", user_id)
            
            user_email = str(user.email)
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] User email: {user_email}")
            
            # Get user's active categories with descriptions
            categories = await self.category_repository.find_active_by_user_id(user_id)
            
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Active categories: {[cat.name for cat in categories]}")
            
            # Get all inbox emails for the user by email address
            emails = await self.email_repository.find_by_recipient(EmailAddress.create(user_email), limit=1000)
            inbox_emails = [email for email in emails if email.email_type.value == "inbox"]
            
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Found {len(inbox_emails)} inbox emails to re-categorize")
            
            recategorized_count = 0
            
            for email in inbox_emails:
                # Re-categorize the email based on current categories with descriptions
                new_category = self._determine_category_with_ai(email, categories)
                if new_category != email.category:
                    print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Email {email.id}: {email.category} -> {new_category}")
                    email.update_category(new_category)
                    await self.email_repository.update(email)
                    recategorized_count += 1
                else:
                    print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Email {email.id}: no change needed ({email.category})")
            
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Re-categorized {recategorized_count} emails")
            return recategorized_count
            
        except Exception as e:
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Error in execute: {e}")
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Full traceback: {traceback.format_exc()}")
            raise
    
    def _determine_category_with_ai(self, email, categories) -> str:
        """Determine the best category for an email using AI with category descriptions"""
        print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] _determine_category_with_ai called for email {email.id}")
        
        # If LLM service is available and we have categories with descriptions, use AI
        if self.llm_service and categories:
            try:
                # Prepare categories for AI
                category_data = []
                for cat in categories:
                    category_data.append({
                        'name': cat.name,
                        'description': cat.description or f"General {cat.name.lower()} related emails"
                    })
                
                print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Using AI categorization with {len(category_data)} categories")
                
                # Use AI to categorize
                ai_category = self.llm_service.categorize_email_with_categories(
                    email_content=email.body or "",
                    email_subject=email.subject or "",
                    sender=str(email.sender),
                    recipient=str(email.recipients[0]) if email.recipients else "",
                    categories=category_data
                )
                
                print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] AI suggested category: {ai_category}")
                return ai_category
                
            except Exception as e:
                print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] AI categorization failed: {e}")
                # Fall back to keyword-based categorization
                pass
        
        # Fallback to keyword-based categorization
        print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Using fallback keyword-based categorization")
        category_names = [cat.name.lower() for cat in categories]
        return self._determine_category(email, category_names)
    
    def _determine_category(self, email, category_names: List[str]) -> str:
        """Determine the best category for an email based on available categories with enhanced precision"""
        # Combine subject and body for analysis
        email_content = f"{email.subject} {email.body}".lower()
        
        # Enhanced keywords with weights and context
        category_keywords = {
            "work": {
                "high_weight": ["meeting", "deadline", "project", "presentation", "report", "client", "business"],
                "medium_weight": ["work", "office", "team", "collaboration", "agenda", "minutes", "proposal"],
                "low_weight": ["schedule", "update", "review", "discussion", "planning"]
            },
            "amazon": {
                "high_weight": ["amazon", "order", "shipping", "delivery", "tracking", "package"],
                "medium_weight": ["purchase", "product", "item", "shipment", "arrival"],
                "low_weight": ["buy", "bought", "received", "arrived"]
            },
            "mastercard": {
                "high_weight": ["mastercard", "credit card", "payment", "transaction", "charge"],
                "medium_weight": ["statement", "account", "balance", "billing"],
                "low_weight": ["bank", "financial", "money"]
            },
            "personal": {
                "high_weight": ["family", "friend", "birthday", "anniversary", "love", "party"],
                "medium_weight": ["personal", "home", "dinner", "lunch", "coffee"],
                "low_weight": ["meet", "catch up", "visit"]
            },
            "finance": {
                "high_weight": ["bank", "account", "balance", "transfer", "investment", "loan"],
                "medium_weight": ["financial", "money", "budget", "expense", "income"],
                "low_weight": ["payment", "transaction", "statement"]
            },
            "shopping": {
                "high_weight": ["purchase", "buy", "sale", "discount", "coupon", "deal"],
                "medium_weight": ["store", "shop", "retail", "offer", "promotion"],
                "low_weight": ["product", "item", "price", "cost"]
            },
            "codeforces": {
                "high_weight": ["codeforces", "contest", "problem", "submission", "rating", "div"],
                "medium_weight": ["algorithm", "programming", "coding", "solution", "test"],
                "low_weight": ["code", "program", "challenge", "competition"]
            },
            "uncategorized": {
                "high_weight": ["uncategorized", "unknown", "misc", "other"],
                "medium_weight": [],
                "low_weight": []
            }
        }
        
        # Find the best matching category
        best_match = None
        best_score = 0
        
        for category_name in category_names:
            total_score = 0
            
            # Check for direct category name match (high weight)
            if category_name in email_content:
                total_score += 10
            
            # Check for category-specific keywords
            if category_name in category_keywords:
                keywords = category_keywords[category_name]
                
                # High weight keywords (3 points each)
                for keyword in keywords["high_weight"]:
                    if keyword in email_content:
                        total_score += 3
                
                # Medium weight keywords (2 points each)
                for keyword in keywords["medium_weight"]:
                    if keyword in email_content:
                        total_score += 2
                
                # Low weight keywords (1 point each)
                for keyword in keywords["low_weight"]:
                    if keyword in email_content:
                        total_score += 1
            
            # Additional context-based scoring
            total_score += self._calculate_context_score(email, category_name)
            
            print(f"🔧 DEBUG: [RecategorizeEmailsUseCase] Email {email.id} category '{category_name}' score: {total_score}")
            
            if total_score > best_score:
                best_score = total_score
                best_match = category_name
        
        # Return the best match or 'uncategorized' as fallback
        return best_match if best_match else "uncategorized" 