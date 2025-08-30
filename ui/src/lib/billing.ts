import { loadStripe, Stripe } from '@stripe/stripe-js';
import pricingData from '../data/pricing.json';
import { isFeatureEnabled } from './featureFlags';

// Types for billing system
export interface PricingTier {
  id: string;
  name: string;
  monthly: number;
  yearly: number;
  limits: {
    projects: number;
    buildHours: number;
    storageGB: number;
    embeddingsMB?: number;
  };
  features: string[];
  description: string;
  ctaText: string;
  ctaVariant: 'outline' | 'default';
}

export interface Subscription {
  id: string;
  status: 'trialing' | 'active' | 'past_due' | 'canceled' | 'incomplete' | 'incomplete_expired' | 'unpaid';
  tier: string;
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelAtPeriodEnd: boolean;
  trialEnd?: Date;
  metadata: Record<string, any>;
}

export interface Customer {
  id: string;
  email: string;
  name?: string;
  subscription?: Subscription;
  metadata: Record<string, any>;
}

export interface CheckoutSession {
  id: string;
  url: string;
  customerId: string;
  successUrl: string;
  cancelUrl: string;
  metadata: Record<string, any>;
}

// Billing service class
export class BillingService {
  private stripe: Stripe | null = null;
  private readonly apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.initializeStripe();
  }

  private async initializeStripe() {
    const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
    if (stripePublishableKey) {
      this.stripe = await loadStripe(stripePublishableKey);
    }
  }

  // Get pricing tiers from the centralized pricing data
  getPricingTiers(): PricingTier[] {
    return pricingData.tiers;
  }

  // Get specific tier by ID
  getTierById(tierId: string): PricingTier | undefined {
    return pricingData.tiers.find(tier => tier.id === tierId);
  }

  // Get tier limits for enforcement
  getTierLimits(tierId: string) {
    const tier = this.getTierById(tierId);
    return tier?.limits || { projects: 1, buildHours: 5, storageGB: 1, embeddingsMB: 100 };
  }

  // Create checkout session for subscription
  async createCheckoutSession(
    tierId: string,
    billingPeriod: 'monthly' | 'yearly',
    successUrl: string,
    cancelUrl: string,
    customerId?: string
  ): Promise<CheckoutSession> {
    // Check if billing v2 is enabled
    if (!isFeatureEnabled('billing_v2')) {
      throw new Error('Billing v2 is not enabled. Please contact support.');
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/billing/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({
          tier: tierId,
          billing_period: billingPeriod,
          success_url: successUrl,
          cancel_url: cancelUrl,
          customer_id: customerId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create checkout session: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating checkout session:', error);
      throw error;
    }
  }

  // Redirect to Stripe checkout
  async redirectToCheckout(session: CheckoutSession): Promise<void> {
    if (!this.stripe) {
      throw new Error('Stripe not initialized');
    }

    const { error } = await this.stripe.redirectToCheckout({
      sessionId: session.id,
    });

    if (error) {
      throw error;
    }
  }

  // Create customer portal session
  async createCustomerPortalSession(returnUrl: string): Promise<string> {
    // Check if billing v2 is enabled
    if (!isFeatureEnabled('billing_v2')) {
      throw new Error('Billing v2 is not enabled. Please contact support.');
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/billing/create-portal-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({
          return_url: returnUrl,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create portal session: ${response.statusText}`);
      }

      const { url } = await response.json();
      return url;
    } catch (error) {
      console.error('Error creating portal session:', error);
      throw error;
    }
  }

  // Get customer subscription status
  async getCustomerSubscription(customerId: string): Promise<Subscription | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/billing/subscription/status/${customerId}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No subscription found
        }
        throw new Error(`Failed to get subscription: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting subscription:', error);
      return null;
    }
  }

  // Check if user has access to a feature
  hasFeatureAccess(subscription: Subscription | null, feature: string): boolean {
    if (!subscription || subscription.status !== 'active') {
      return false;
    }

    const tier = this.getTierById(subscription.tier);
    if (!tier) {
      return false;
    }

    // Check feature access based on tier
    switch (feature) {
      case 'custom_domain':
        return ['STARTER', 'PRO', 'SCALE'].includes(subscription.tier);
      case 'advanced_agents':
        return ['PRO', 'SCALE'].includes(subscription.tier);
      case 'isolated_database':
        return ['SCALE'].includes(subscription.tier);
      case 'priority_support':
        return ['PRO', 'SCALE'].includes(subscription.tier);
      default:
        return true; // Basic features available to all paid tiers
    }
  }

  // Check usage limits
  checkUsageLimits(subscription: Subscription | null, usage: Record<string, number>): {
    withinLimits: boolean;
    exceededFeatures: string[];
    remaining: Record<string, number>;
  } {
    if (!subscription || subscription.status !== 'active') {
      return {
        withinLimits: false,
        exceededFeatures: ['subscription'],
        remaining: { projects: 0, buildHours: 0, storageGB: 0 },
      };
    }

    const tier = this.getTierById(subscription.tier);
    if (!tier) {
      return {
        withinLimits: false,
        exceededFeatures: ['tier'],
        remaining: { projects: 0, buildHours: 0, storageGB: 0 },
      };
    }

    const limits = tier.limits;
    const exceededFeatures: string[] = [];
    const remaining: Record<string, number> = {};

    // Check projects limit
    if (usage.projects > limits.projects) {
      exceededFeatures.push('projects');
    }
    remaining.projects = Math.max(0, limits.projects - usage.projects);

    // Check build hours limit
    if (limits.buildHours !== -1 && usage.buildHours > limits.buildHours) {
      exceededFeatures.push('buildHours');
    }
    remaining.buildHours = limits.buildHours === -1 ? -1 : Math.max(0, limits.buildHours - usage.buildHours);

    // Check storage limit
    if (usage.storageGB > limits.storageGB) {
      exceededFeatures.push('storage');
    }
    remaining.storageGB = Math.max(0, limits.storageGB - usage.storageGB);

    return {
      withinLimits: exceededFeatures.length === 0,
      exceededFeatures,
      remaining,
    };
  }

  // Get upgrade options for current tier
  getUpgradeOptions(currentTierId: string): PricingTier[] {
    const currentTier = this.getTierById(currentTierId);
    if (!currentTier) {
      return this.getPricingTiers().filter(tier => tier.id !== 'FREE');
    }

    const tierOrder = ['FREE', 'STARTER', 'PRO', 'SCALE'];
    const currentIndex = tierOrder.indexOf(currentTierId);
    
    return this.getPricingTiers()
      .filter(tier => tierOrder.indexOf(tier.id) > currentIndex)
      .sort((a, b) => tierOrder.indexOf(a.id) - tierOrder.indexOf(b.id));
  }

  // Calculate annual savings
  calculateAnnualSavings(tier: PricingTier): number {
    const monthlyCost = tier.monthly * 12;
    const yearlyCost = tier.yearly;
    return monthlyCost - yearlyCost;
  }

  // Get annual discount percentage
  getAnnualDiscount(tier: PricingTier): number {
    const monthlyCost = tier.monthly * 12;
    const yearlyCost = tier.yearly;
    return ((monthlyCost - yearlyCost) / monthlyCost) * 100;
  }

  // Private helper methods
  private getAuthToken(): string {
    // Get auth token from your auth system
    // This should integrate with your existing authentication
    return localStorage.getItem('auth_token') || '';
  }
}

// Export singleton instance
export const billingService = new BillingService();

// Export types for use in components
export type { PricingTier, Subscription, Customer, CheckoutSession };
