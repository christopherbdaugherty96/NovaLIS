# Monetization Strategy & Future Business Options

**Status:** *Strategy Inventory (Not Current Priority)*  
**Audience:** Core Team / Future Reference  
**License Alignment:** Apache 2.0 – This document outlines commercial paths that preserve the open-source core.

---

## Executive Summary

Nova LIS has a unique and commercially defensible differentiator: **the separation of intelligence from authority**. This document catalogs potential paths to sustainability and revenue. **It is not a directive for immediate action.** The current priority remains Tier 1 execution: making Nova installable, usable, and valuable enough that users return weekly.

*Use this document to understand what "success" might unlock, then close it and return to the roadmap.*

---

## The Core Value Proposition (Why Anyone Would Pay)

- **Trust & Governance:** Users and enterprises are increasingly wary of "black box" AI agents that act autonomously without oversight. Nova's Governor pattern provides auditability, permissioning, and controlled execution.
- **Local-First Sovereignty:** Nova runs where the user wants it—their machine, their data, their control.
- **Opinionated Architecture:** The separation of intelligence (thinking) from authority (doing) is not a marketing slogan; it's a technical constraint that creates a safer, more reliable AI workspace.

---

## Monetization Pathways (Tiered by Horizon)

### 🟢 Near-Term Horizon (Now – 6 Months)
*Focus: Validation & Friction Reduction*

| Opportunity | Description | Prerequisites | Revenue Model |
| :--- | :--- | :--- | :--- |
| **Paid Setup & Onboarding** | Handle installation, environment configuration, and first-use training for individuals or small teams. | Current friction in `install.sh` and dependency management. | One-time service fee ($200–$500) |
| **Priority Support Tiers** | Offer guaranteed response times and a private support channel for power users. | A small, engaged user base with recurring questions. | Monthly subscription ($25–$100/mo) |
| **Workflow Integration Consulting** | Help businesses wire Nova into their existing tools (Obsidian, Notion, local file servers). | Demonstrated value of the `read-only second-opinion` and `open` features. | Project-based hourly or fixed fee |

> **Guidance:** Treat these as **feedback loops** for the product. Every paid setup reveals a bug in the installer. Every support ticket reveals a gap in the documentation.

### 🟡 Mid-Term Horizon (6 – 18 Months)
*Focus: Scale & Accessibility*

| Opportunity | Description | Prerequisites | Revenue Model |
| :--- | :--- | :--- | :--- |
| **Hosted/SaaS Version (Nova Cloud)** | A managed web version of Nova LIS. Eliminates local install friction and provides always-on availability. | Stable core API; clear path to sandboxed worker execution in cloud environment. | Freemium subscription (Free tier with query caps; Pro tier $10–$30/mo) |
| **Commercial Plugin Connectors** | Premium "Governor-approved" connectors for enterprise tools (Jira, Salesforce, Google Workspace). | A defined plugin/connector interface and governance layer robust enough for production. | One-time purchase or subscription for specific connectors. |
| **Enterprise Commercial License** | Offer a proprietary license for large organizations requiring indemnification, warranties, and SLAs. | Established user base inside enterprises; legal review of dual-licensing structure. | Annual license fee based on seat count. |

> **Guidance:** The SaaS path is attractive but introduces operational overhead (hosting costs, security, uptime). **Decision Gate:** Do not commit to SaaS until the local installer works flawlessly for 90% of new users on clean OS environments.

### 🔴 Long-Term Horizon (18+ Months)
*Focus: Ecosystem & Specialization*

| Opportunity | Description | Prerequisites | Revenue Model |
| :--- | :--- | :--- | :--- |
| **Nova Box Appliance** | A pre-configured hardware device (e.g., Intel NUC) shipped with Nova LIS ready to run on a local network. | Stable software stack with zero-touch maintenance. | Hardware sale with recurring software update subscription. |
| **Vertical Solutions** | Specialized editions: *Nova for Legal* (case law summarization), *Nova for Finance* (governed data analysis), *Nova for Project Management*. | Proven product-market fit in the general tool; deep understanding of a specific industry workflow. | Tiered SaaS or outcome-based pricing. |

> **Guidance:** Hardware is a heavy operational lift (manufacturing, returns, supply chain). Vertical solutions require deep domain expertise. These are **aspirational outcomes** of a successful general platform.

---

## Critical Constraints & Decision Gates

To prevent premature monetization from derailing the roadmap, the following gates must be met before pursuing the respective tiers:

| Tier | Gate Condition |
| :--- | :--- |
| **Near-Term** | *(No gate - these are services that aid current development)* |
| **Mid-Term** | 1. Installer success rate > 90% on clean MacOS/Windows/Linux.<br>2. 10+ Weekly Active Users (not including creator).<br>3. At least one successful "mutation" performed by an external user without hand-holding. |
| **Long-Term** | 1. 100+ Active Users or a signed Enterprise pilot.<br>2. Feature stability across 3 major releases. |

---

## Final Word

This document is **strategy inventory**. It is smart and encouraging, but it is not the main mission.

**The highest-value revenue move right now is making Nova useful enough that people would want to pay for anything at all.**

Return to `ROADMAP.md`. Return to the installer. Return to the first mutation.