#!/usr/bin/env python3
"""
Category Management Test Script

This script demonstrates the category management feature including:
1. Creating categories
2. Listing categories
3. Updating categories
4. Deleting categories
5. Re-categorizing emails
6. Getting emails by category
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List


class CategoryManagementTester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session_id = None
        self.user_email = None
        
    async def authenticate(self, session_id: str, user_email: str):
        """Set authentication credentials"""
        self.session_id = session_id
        self.user_email = user_email
        print(f"🔐 Authenticated as: {user_email}")
        print(f"🔑 Session ID: {session_id}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.session_id}",
            "Content-Type": "application/json"
        }
    
    async def create_category(self, name: str, description: str = None, color: str = None) -> Dict[str, Any]:
        """Create a new category"""
        print(f"\n📝 Creating category: {name}")
        
        data = {"name": name}
        if description:
            data["description"] = description
        if color:
            data["color"] = color
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/categories",
                headers=self._get_headers(),
                json=data
            ) as response:
                result = await response.json()
                print(f"✅ Category created: {result}")
                return result
    
    async def list_categories(self, include_inactive: bool = False) -> Dict[str, Any]:
        """List all categories"""
        print(f"\n📋 Listing categories (include_inactive: {include_inactive})")
        
        params = {"include_inactive": include_inactive}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/categories",
                headers=self._get_headers(),
                params=params
            ) as response:
                result = await response.json()
                print(f"✅ Found {result['total_count']} categories:")
                for category in result['categories']:
                    print(f"   - {category['name']} ({category['id']})")
                return result
    
    async def update_category(self, category_id: str, **updates) -> Dict[str, Any]:
        """Update a category"""
        print(f"\n✏️ Updating category: {category_id}")
        print(f"   Updates: {updates}")
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/categories/{category_id}",
                headers=self._get_headers(),
                json=updates
            ) as response:
                result = await response.json()
                print(f"✅ Category updated: {result}")
                return result
    
    async def delete_category(self, category_id: str) -> Dict[str, Any]:
        """Delete a category"""
        print(f"\n🗑️ Deleting category: {category_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/categories/{category_id}",
                headers=self._get_headers()
            ) as response:
                result = await response.json()
                print(f"✅ Category deleted: {result}")
                return result
    
    async def recategorize_emails(self) -> Dict[str, Any]:
        """Re-categorize all emails"""
        print(f"\n🔄 Re-categorizing emails...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/categories/recategorize-emails",
                headers=self._get_headers()
            ) as response:
                result = await response.json()
                print(f"✅ Re-categorization complete: {result}")
                return result
    
    async def get_emails_by_category(self, category_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get emails by category"""
        print(f"\n📧 Getting emails for category: {category_name}")
        
        params = {"limit": limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails/category/{category_name}",
                headers=self._get_headers(),
                params=params
            ) as response:
                result = await response.json()
                print(f"✅ Found {result['total_count']} emails in category '{category_name}':")
                for email in result['emails']:
                    print(f"   - {email['subject'][:50]}... (ID: {email['id']})")
                return result
    
    async def get_inbox_emails(self, limit: int = 10) -> Dict[str, Any]:
        """Get inbox emails"""
        print(f"\n📥 Getting inbox emails...")
        
        params = {"limit": limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/emails/inbox",
                headers=self._get_headers(),
                params=params
            ) as response:
                result = await response.json()
                print(f"✅ Found {result['total_count']} inbox emails:")
                for email in result['emails']:
                    category = email.get('category', 'uncategorized')
                    print(f"   - {email['subject'][:50]}... (Category: {category})")
                return result


async def main():
    """Main test function"""
    print("🚀 Category Management Test Script")
    print("=" * 50)
    
    # Initialize tester
    tester = CategoryManagementTester()
    
    # You need to provide your session ID and user email
    # Get these from your OAuth authentication flow
    session_id = input("Enter your session ID: ").strip()
    user_email = input("Enter your user email: ").strip()
    
    if not session_id or not user_email:
        print("❌ Session ID and user email are required")
        return
    
    await tester.authenticate(session_id, user_email)
    
    try:
        # Step 1: Create some categories
        print("\n" + "="*50)
        print("STEP 1: Creating Categories")
        print("="*50)
        
        work_category = await tester.create_category(
            name="Work",
            description="Work-related emails",
            color="#FF5733"
        )
        
        amazon_category = await tester.create_category(
            name="Amazon",
            description="Amazon orders and deliveries",
            color="#33FF57"
        )
        
        mastercard_category = await tester.create_category(
            name="Mastercard",
            description="Credit card statements and transactions",
            color="#3357FF"
        )
        
        personal_category = await tester.create_category(
            name="Personal",
            description="Personal and family emails",
            color="#F3FF33"
        )
        
        # Step 2: List categories
        print("\n" + "="*50)
        print("STEP 2: Listing Categories")
        print("="*50)
        
        categories = await tester.list_categories()
        
        # Step 3: Update a category
        print("\n" + "="*50)
        print("STEP 3: Updating Category")
        print("="*50)
        
        if categories['categories']:
            category_to_update = categories['categories'][0]
            await tester.update_category(
                category_to_update['id'],
                description=f"Updated: {category_to_update['description']}",
                color="#FF33F3"
            )
        
        # Step 4: Check current inbox emails
        print("\n" + "="*50)
        print("STEP 4: Checking Current Inbox Emails")
        print("="*50)
        
        await tester.get_inbox_emails(limit=5)
        
        # Step 5: Re-categorize emails
        print("\n" + "="*50)
        print("STEP 5: Re-categorizing Emails")
        print("="*50)
        
        recat_result = await tester.recategorize_emails()
        
        # Step 6: Check emails by category
        print("\n" + "="*50)
        print("STEP 6: Checking Emails by Category")
        print("="*50)
        
        for category_name in ["Work", "Amazon", "Mastercard", "Personal"]:
            await tester.get_emails_by_category(category_name, limit=3)
        
        # Step 7: Delete a category (optional)
        print("\n" + "="*50)
        print("STEP 7: Deleting Category (Optional)")
        print("="*50)
        
        delete_choice = input("Do you want to delete a category? (y/n): ").strip().lower()
        if delete_choice == 'y' and categories['categories']:
            category_to_delete = categories['categories'][-1]  # Delete the last one
            await tester.delete_category(category_to_delete['id'])
            
            # Re-categorize emails after deletion
            print("\n🔄 Re-categorizing emails after category deletion...")
            await tester.recategorize_emails()
        
        print("\n" + "="*50)
        print("✅ Category Management Test Complete!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 