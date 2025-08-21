#!/usr/bin/env python3
"""
Marketplace Routes for API Gateway
Night XX: Marketplace functionality with product listings, demos, and onboarding

This module provides:
- Product listing and filtering
- Product demo details
- Product onboarding flow
- Marketplace statistics
"""

import os
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel, Field
import asyncpg

from tenant_db import TenantDatabase, TenantContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

# Database connection
tenant_db = TenantDatabase()

# Mock products data - in production, this would come from database
MOCK_PRODUCTS = [
    {
        "id": "1",
        "name": "TaskFlow Pro",
        "description": "AI-powered project management with automated task prioritization and team collaboration.",
        "category": "Productivity",
        "price": "$29/month",
        "rating": 4.8,
        "users": 1250,
        "status": "live",
        "image": "/api/placeholder/300/200",
        "features": ["AI Task Prioritization", "Team Collaboration", "Time Tracking", "Analytics Dashboard"],
        "techStack": ["React", "Node.js", "PostgreSQL", "OpenAI API"],
        "demo_available": True,
        "demo_url": "https://demo.taskflow.com",
        "screenshots": [
            "https://demo.taskflow.com/screenshot1.png",
            "https://demo.taskflow.com/screenshot2.png"
        ],
        "pricing_plans": [
            {"name": "Starter", "price": "$19/month", "features": ["Basic AI", "5 Projects", "Email Support"]},
            {"name": "Pro", "price": "$29/month", "features": ["Advanced AI", "Unlimited Projects", "Priority Support"]},
            {"name": "Enterprise", "price": "$99/month", "features": ["Custom AI", "White-label", "24/7 Support"]}
        ]
    },
    {
        "id": "2",
        "name": "LeadGen AI",
        "description": "Automated lead generation and qualification using machine learning algorithms.",
        "category": "Sales",
        "price": "$49/month",
        "rating": 4.6,
        "users": 890,
        "status": "live",
        "image": "/api/placeholder/300/200",
        "features": ["Lead Scoring", "Email Automation", "CRM Integration", "Analytics"],
        "techStack": ["Vue.js", "Python", "MongoDB", "TensorFlow"],
        "demo_available": True,
        "demo_url": "https://demo.leadgen.ai",
        "screenshots": [
            "https://demo.leadgen.ai/dashboard.png",
            "https://demo.leadgen.ai/leads.png"
        ],
        "pricing_plans": [
            {"name": "Basic", "price": "$29/month", "features": ["1000 Leads", "Basic Scoring", "Email Support"]},
            {"name": "Pro", "price": "$49/month", "features": ["5000 Leads", "Advanced Scoring", "Priority Support"]},
            {"name": "Enterprise", "price": "$149/month", "features": ["Unlimited Leads", "Custom Models", "Dedicated Support"]}
        ]
    },
    {
        "id": "3",
        "name": "ContentCraft",
        "description": "AI content creation platform for blogs, social media, and marketing campaigns.",
        "category": "Marketing",
        "price": "$39/month",
        "rating": 4.7,
        "users": 2100,
        "status": "live",
        "image": "/api/placeholder/300/200",
        "features": ["AI Writing Assistant", "SEO Optimization", "Content Calendar", "Performance Analytics"],
        "techStack": ["Next.js", "TypeScript", "Supabase", "GPT-4"],
        "demo_available": True,
        "demo_url": "https://demo.contentcraft.ai",
        "screenshots": [
            "https://demo.contentcraft.ai/editor.png",
            "https://demo.contentcraft.ai/analytics.png"
        ],
        "pricing_plans": [
            {"name": "Starter", "price": "$19/month", "features": ["50 Articles", "Basic SEO", "Community Support"]},
            {"name": "Professional", "price": "$39/month", "features": ["200 Articles", "Advanced SEO", "Email Support"]},
            {"name": "Agency", "price": "$99/month", "features": ["1000 Articles", "Custom SEO", "Priority Support"]}
        ]
    },
    {
        "id": "4",
        "name": "DataViz Studio",
        "description": "Interactive data visualization and business intelligence platform.",
        "category": "Analytics",
        "price": "$79/month",
        "rating": 4.9,
        "users": 650,
        "status": "beta",
        "image": "/api/placeholder/300/200",
        "features": ["Interactive Charts", "Real-time Data", "Custom Dashboards", "Export Options"],
        "techStack": ["React", "D3.js", "FastAPI", "ClickHouse"],
        "demo_available": True,
        "demo_url": "https://demo.dataviz.studio",
        "screenshots": [
            "https://demo.dataviz.studio/dashboard.png",
            "https://demo.dataviz.studio/charts.png"
        ],
        "pricing_plans": [
            {"name": "Basic", "price": "$39/month", "features": ["5 Dashboards", "Basic Charts", "Email Support"]},
            {"name": "Professional", "price": "$79/month", "features": ["Unlimited Dashboards", "Advanced Charts", "Priority Support"]},
            {"name": "Enterprise", "price": "$199/month", "features": ["Custom Charts", "API Access", "Dedicated Support"]}
        ]
    },
    {
        "id": "5",
        "name": "SecureChat",
        "description": "End-to-end encrypted messaging platform for enterprise teams.",
        "category": "Communication",
        "price": "$19/month",
        "rating": 4.5,
        "users": 3200,
        "status": "live",
        "image": "/api/placeholder/300/200",
        "features": ["End-to-End Encryption", "File Sharing", "Video Calls", "Admin Controls"],
        "techStack": ["React Native", "WebRTC", "Signal Protocol", "Redis"],
        "demo_available": False,
        "demo_url": None,
        "screenshots": [],
        "pricing_plans": [
            {"name": "Team", "price": "$19/month", "features": ["Unlimited Users", "File Sharing", "Community Support"]},
            {"name": "Business", "price": "$49/month", "features": ["Admin Controls", "Audit Logs", "Priority Support"]},
            {"name": "Enterprise", "price": "$99/month", "features": ["Custom Branding", "Advanced Security", "24/7 Support"]}
        ]
    },
    {
        "id": "6",
        "name": "InvoiceFlow",
        "description": "Automated invoicing and payment processing for small businesses.",
        "category": "Finance",
        "price": "$25/month",
        "rating": 4.4,
        "users": 1800,
        "status": "live",
        "image": "/api/placeholder/300/200",
        "features": ["Auto-Invoicing", "Payment Processing", "Expense Tracking", "Tax Calculations"],
        "techStack": ["Angular", "Java", "MySQL", "Stripe API"],
        "demo_available": True,
        "demo_url": "https://demo.invoiceflow.com",
        "screenshots": [
            "https://demo.invoiceflow.com/invoices.png",
            "https://demo.invoiceflow.com/reports.png"
        ],
        "pricing_plans": [
            {"name": "Solo", "price": "$15/month", "features": ["100 Invoices", "Basic Reporting", "Email Support"]},
            {"name": "Business", "price": "$25/month", "features": ["Unlimited Invoices", "Advanced Reporting", "Priority Support"]},
            {"name": "Enterprise", "price": "$75/month", "features": ["Multi-business", "Custom Templates", "Dedicated Support"]}
        ]
    }
]

class ProductResponse(BaseModel):
    """Product response model"""
    id: str
    name: str
    description: str
    category: str
    price: str
    rating: float
    users: int
    status: str
    image: str
    features: List[str]
    techStack: List[str]
    demo_available: bool
    demo_url: Optional[str]
    screenshots: List[str]
    pricing_plans: List[Dict[str, Any]]

class ProductDemoResponse(BaseModel):
    """Product demo response model"""
    product_id: str
    product_name: str
    demo_url: str
    screenshots: List[str]
    features: List[str]
    pricing_plans: List[Dict[str, Any]]
    description: str

class OnboardingResponse(BaseModel):
    """Product onboarding response model"""
    product_id: str
    product_name: str
    onboarding_id: str
    status: str
    next_steps: List[str]
    redirect_url: str

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: Optional[str] = Query("rating", description="Sort by: rating, users, name"),
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get all marketplace products with optional filtering and sorting"""
    try:
        # Filter products
        filtered_products = MOCK_PRODUCTS.copy()

        if category and category != "All":
            filtered_products = [p for p in filtered_products if p["category"] == category]

        if search:
            search_lower = search.lower()
            filtered_products = [
                p for p in filtered_products
                if search_lower in p["name"].lower() or search_lower in p["description"].lower()
            ]

        # Sort products
        if sort_by == "rating":
            filtered_products.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "users":
            filtered_products.sort(key=lambda x: x["users"], reverse=True)
        elif sort_by == "name":
            filtered_products.sort(key=lambda x: x["name"])

        # Convert to response model
        products = []
        for product in filtered_products:
            products.append(ProductResponse(**product))

        return products

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get products: {str(e)}")

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get a specific product by ID"""
    try:
        # Find product
        product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductResponse(**product)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get product: {str(e)}")

@router.get("/products/{product_id}/demo", response_model=ProductDemoResponse)
async def get_product_demo(
    product_id: str,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get product demo details"""
    try:
        # Find product
        product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if not product["demo_available"]:
            raise HTTPException(status_code=404, detail="Demo not available for this product")

        return ProductDemoResponse(
            product_id=product["id"],
            product_name=product["name"],
            demo_url=product["demo_url"],
            screenshots=product["screenshots"],
            features=product["features"],
            pricing_plans=product["pricing_plans"],
            description=product["description"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product demo for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get product demo: {str(e)}")

@router.post("/products/{product_id}/onboard", response_model=OnboardingResponse)
async def start_product_onboarding(
    product_id: str,
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Start product onboarding process"""
    try:
        # Find product
        product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Generate onboarding ID
        onboarding_id = f"onboard_{product_id}_{int(datetime.now().timestamp())}"

        # Store onboarding record (in production, this would be in database)
        logger.info(f"Started onboarding for product {product_id} by user {x_user_id}")

        return OnboardingResponse(
            product_id=product_id,
            product_name=product["name"],
            onboarding_id=onboarding_id,
            status="initiated",
            next_steps=[
                "Complete signup with selected product",
                "Configure account settings",
                "Import data (if applicable)",
                "Start free trial"
            ],
            redirect_url=f"/signup?product={product_id}&productName={product['name']}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting product onboarding for {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start product onboarding: {str(e)}")

@router.get("/stats")
async def get_marketplace_stats(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get marketplace statistics"""
    try:
        total_products = len(MOCK_PRODUCTS)
        live_products = len([p for p in MOCK_PRODUCTS if p["status"] == "live"])
        total_users = sum(p["users"] for p in MOCK_PRODUCTS)
        avg_rating = sum(p["rating"] for p in MOCK_PRODUCTS) / total_products

        categories = {}
        for product in MOCK_PRODUCTS:
            cat = product["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        return {
            "total_products": total_products,
            "live_products": live_products,
            "beta_products": len([p for p in MOCK_PRODUCTS if p["status"] == "beta"]),
            "total_users": total_users,
            "average_rating": round(avg_rating, 2),
            "categories": categories,
            "trending_products": [p for p in MOCK_PRODUCTS if p["users"] > 1000]
        }

    except Exception as e:
        logger.error(f"Error getting marketplace stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get marketplace stats: {str(e)}")

@router.get("/categories")
async def get_categories(
    x_tenant_id: str = Header(..., description="Tenant ID"),
    x_user_id: Optional[str] = Header(None, description="User ID")
):
    """Get all product categories"""
    try:
        categories = list(set(p["category"] for p in MOCK_PRODUCTS))
        categories.sort()

        return {
            "categories": ["All"] + categories
        }

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")
