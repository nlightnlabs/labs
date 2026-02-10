# Project management App:
Please review the current app folder architecture and structure and add / integrate a module that helps me management projects according to the requirements below.

folder path: /Users/avikghosh/Documents/nlightn/Solution Management/Code/labs

## UI instructions:
- Add a menu item in the main Sidbare.tsx component that says "Projects" in the same section as as the existing Data and Chat items.  When somone cliks on the the projects item, render the entire project appliction on the main component to thte right.
- Keep the styleing and design framework consistent

## Backend instructions:
- The object library and all data models are managed by data tables in a postgres.  
- Do not create any new object models hard coded in this app
- Assume objects like Initiatives, Workstreams, Tasks, Assignments, Deliverables, Milestones, etc. are all created in the backend. Please identify  any additional object you think are needed and I will add them later to the backend.  If needed provide a placeholder for them.

## Product Business Requirements:
- Multi-project setup with procurement-specific templates (initiation → sourcing → evaluation → negotiation → contracting   → implementation)
- Hierarchical work streams, detailed plans, dependencies, milestones, and enforced stage gates with client/ internal MainePointe approvals
- Assign tasks to internal teams, clients, or vendors (role-based permissions)
- Daily tracking: time logs, progress %, comments, attachments, recurring items
- Views: Kanban, Gantt, calendar; reminders, alerts, overdue flags
- Secure external portal for clients: view/edit assigned tasks, submit docs, provide feedback
- Real-time comments, chat, shared editing, document version control
- Team allocation & availability calendars
- Engagement budget tracking, expense logging, variance alerts
- Integrated Gantt/timeline views: planned vs. actual, phase status, upcoming milestones
- Standard Reporting and dashboards: % complete, delays, health indicators
- Custom dashboards
- Narrative-driven outputs: journey maps, annotated timelines, “before/after” comparisons, value flow diagrams
- Interactive elements: progress arcs, Sankey for benefits, call-outs for key insights & “so-what” messaging
- Optimized for client meetings: branded exports (PDF, PPT), executive summaries, slide-like storytelling layouts
- Overall Modern, visually compelling UX suitable for client-facing presentations; storytelling layouts, branded look & feel, "slide-like" experience when walking clients through status & results
- Log & visualize quantifiable benefits (cost savings, ROI curves, supplier scores, risk reduction)
- Trend analysis, benchmarks, success narratives to justify value & support renewals/upsell
- Supplier database with performance history & scoring
- RFP/RFQ templates, bid comparison, evaluation matrices
- Contract lifecycle tracking, alerts, compliance checklists
- AI integrated into the platform (e.g. Chat, agents,)