# ERP for the Graphic Industry

<p align="center">
  <strong>Integrated Desktop Workflow for Commercial Orders, Prepress, Production Scheduling, and Graphic-Process Coordination</strong>
</p>

<p align="center">
  A Python and PyQt5 operational platform connecting proformas, work orders, production processes, weekly planning, Google Apps Script services, and industrial communication.
</p>

---

## Executive Overview

**ERP for the Graphic Industry** is a specialized desktop application developed to coordinate the operational workflow of a printing and graphic-production company. The system connects the commercial, prepress, and production stages through a shared information flow, reducing fragmented records and improving the traceability of each approved quotation and production order.

The application is implemented in **Python with PyQt5** and communicates through HTTP with a **Google Apps Script** service backed by Google Sheets. This architecture allows commercial data, design milestones, production requirements, process assignments, and scheduled delivery activities to be maintained in a common operational dataset.

In addition to the business workflow, the system includes a background **Modbus TCP server**, providing a foundation for future integration with industrial equipment, supervisory interfaces, production indicators, or shop-floor automation.

---

## Operational Scope

The platform organizes the lifecycle of a graphic-production request across five principal areas:

| Area | Operational Responsibility |
| --- | --- |
| **Commercial** | Creation and editing of approved proformas, customer information, order quantities, descriptions, and delivery commitments. |
| **Diagramming / Prepress** | Registration of artwork reception, designer assignment, prepress progress, customer approval, CTP delivery, and plate preparation. |
| **Production** | Conversion of approved work into production orders, materials, print runs, machines, finishing operations, and process requirements. |
| **Task Scheduling** | Assignment of work orders to dates and specific production processes through an interactive scheduling interface. |
| **Production Planning** | Weekly visualization of scheduled work by process, with navigation between weeks and exportable PDF reports. |

---

## Process Flow

```text
Approved Proforma
       │
       ▼
Commercial Registration
       │
       ▼
Diagramming and Prepress
       │
       ▼
Production Order Definition
       │
       ├── Printing processes
       ├── Finishing processes
       ├── Materials and quantities
       └── Required production resources
       │
       ▼
Task Scheduling by Process and Date
       │
       ▼
Weekly Production Plan and PDF Reporting
```

Each stage contributes information to the same operational record, allowing the organization to follow a job from customer approval to production scheduling.

---

## System Architecture

The project follows a lightweight distributed architecture:

```text
┌──────────────────────────────────────────────┐
│        Python / PyQt5 Desktop Client         │
│                                              │
│  Commercial · Diagramming · Production      │
│  Task Scheduling · Weekly Planning · PDF    │
└──────────────────────┬───────────────────────┘
                       │ HTTP GET / POST
                       ▼
┌──────────────────────────────────────────────┐
│             Google Apps Script API           │
│                                              │
│  Validation · Record management · Routing   │
│  Proforma numbering · OT assignment         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│               Google Sheets                  │
│                                              │
│  Shared operational records and process     │
│  sheets for production coordination         │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│       Background Modbus TCP Interface        │
│                                              │
│  Foundation for industrial-system and       │
│  equipment-level integration                │
└──────────────────────────────────────────────┘
```

---

## Main Application Modules

### Commercial Management

The commercial interface supports the creation and editing of approved proformas. Multiple orders can be entered in one session, and proforma numbering is generated from the shared operational dataset.

Principal data includes:

- Commercial executive.
- Customer.
- Customer classification.
- Product or service description.
- Requested quantity.
- Delivery date.
- Approved proforma number.

The interface communicates with the Apps Script service to retrieve existing proformas and maintain synchronized records.

### Diagramming and Prepress

The diagramming module documents the transition from the commercial request to production-ready artwork.

Tracked milestones include:

- Artwork reception date.
- Assigned designer.
- Prepress completion.
- Artwork submission for approval.
- Customer approval date.
- CTP submission.
- Plate-burning completion.

This stage improves visibility over design dependencies that must be completed before a job can progress to manufacturing.

### Production Management

The production module records the technical definition of the work order, including:

- Work-order number.
- Opening and delivery dates.
- Paper or cardstock specification.
- Sheet quantity.
- Print run.
- Printing-machine requirements.
- Ink, plates, printing type, and number of passes.
- Required post-print and finishing processes.

When a process is selected, the corresponding OT is also registered in its process-specific worksheet, creating a structured production queue.

### Task Scheduling

The scheduling interface loads available OTs by production process and allows them to be assigned to calendar dates.

The module includes:

- Process selection.
- Available and assigned OT lists.
- Drag-and-drop task assignment.
- Calendar-based scheduling.
- Removal or reassignment of scheduled work.
- Background data loading to preserve interface responsiveness.

This separation between process demand and scheduled execution provides a practical operational-planning layer.

### Weekly Production Plan

The production-planning module consolidates assigned work into a weekly matrix organized by process and working day.

Capabilities include:

- Previous- and next-week navigation.
- Monday-to-Friday production overview.
- Process-oriented workload visualization.
- Automatic organization of scheduled OTs.
- Export of the weekly plan to an A4 PDF document.

The resulting report can be distributed to production teams or used during operational-planning meetings.

### API Configuration

The desktop client includes a configurable Apps Script endpoint. The selected URL is persisted through `QSettings`, allowing deployments to update the service address without modifying the application source code.

### Modbus TCP Service

A Modbus TCP server is launched in a background thread when the application starts. The implementation exposes discrete inputs, coils, holding registers, and input registers through a single server context.

This component establishes a technical foundation for future integration with:

- Production machines.
- PLCs or embedded controllers.
- Monitoring dashboards.
- Shop-floor indicators.
- Industrial data-acquisition systems.

---

## Graphic-Production Processes

The current workflow recognizes multiple printing and finishing operations, including:

| Category | Supported Processes |
| --- | --- |
| Printing | XL75, XL-UV, typographic and cylindrical operations. |
| Surface finishing | Varnishing, plastic lamination, localized finishing, and dry embossing. |
| Decorative finishing | Hot stamping. |
| Cutting and forming | Easy Matrix, perforation, and folding. |
| Assembly | Collating, stapling, padding, spiral binding, one-point gluing, three-point gluing, and Tesa-tape bonding. |

Each selected process receives the relevant OT, allowing workload to be organized independently while remaining linked to the primary production record.

---

## Technical Profile

| Category | Implementation |
| --- | --- |
| Application type | Desktop ERP / production-coordination system |
| Primary language | Python |
| User interface | PyQt5 |
| Service communication | HTTP GET and POST through `requests` |
| Backend service | Google Apps Script |
| Operational data layer | Google Sheets |
| Industrial protocol | Modbus TCP through `pymodbus` |
| Document generation | PDF reports through ReportLab |
| Local configuration | `QSettings` |
| Concurrency | `QThread` and asynchronous Modbus execution |
| Packaging support | Resource-path handling compatible with PyInstaller |

---

## Repository Structure

```text
ERP-for-graphic-industry/
├── README.md
├── HERMENCA ERPP/
│   ├── main.py
│   ├── comercial.py
│   ├── diagramacion.py
│   ├── produccion.py
│   ├── taskprogram.py
│   ├── produccionplan.py
│   ├── server.py
│   └── application resources
└── Google Apps Scripts/
    ├── Get.gs
    └── Postman
```

### Principal Components

| File | Responsibility |
| --- | --- |
| `main.py` | Application startup, dashboard, module navigation, API configuration, and Modbus-thread initialization. |
| `comercial.py` | Creation and editing of commercial records and approved proformas. |
| `diagramacion.py` | Diagramming, artwork, approval, CTP, and plate-preparation milestones. |
| `produccion.py` | Work-order definition, material data, print requirements, and finishing-process selection. |
| `taskprogram.py` | Process-based OT scheduling through lists, calendar interaction, and drag-and-drop operations. |
| `produccionplan.py` | Weekly production matrix and PDF export. |
| `server.py` | Asynchronous Modbus TCP server. |
| `Google Apps Scripts/Get.gs` | Read operations, OT loading, assignment, removal, validation, and proforma retrieval. |
| `Google Apps Scripts/Postman` | Write operations for commercial, diagramming, and production data. |

---

## Installation

The project was developed as a Python desktop application. A compatible environment should include Python 3.9 or a validated equivalent.

Install the principal dependencies:

```bash
pip install PyQt5 requests pymodbus reportlab
```

Run the application from the project directory:

```bash
cd "HERMENCA ERPP"
python main.py
```

Before operational use, configure the deployed Google Apps Script endpoint from the application's **API Configuration** module.

---

## Deployment Considerations

A production deployment should externalize environment-specific information and validate the following:

- Google Apps Script deployment permissions.
- Spreadsheet access and worksheet naming.
- API endpoint configuration.
- Network availability and request timeouts.
- Modbus TCP port permissions and firewall rules.
- Local PDF output location.
- Dependency versions and Python environment.
- Packaging resources when generating an executable.

Service URLs, spreadsheet identifiers, and deployment credentials should not be hard-coded in publicly distributed builds.

---

## Engineering Value

The project demonstrates the integration of business-process software with production-planning and industrial-connectivity concepts. Its principal engineering strengths are:

- Domain-specific modeling of the graphic-production workflow.
- Traceability from approved quotation to scheduled manufacturing.
- Modular desktop interfaces for independent departments.
- Shared operational records through a lightweight cloud backend.
- Process-level OT distribution.
- Weekly planning and printable reporting.
- Extensibility toward industrial equipment through Modbus TCP.

---

## Development Status

The repository represents a functional prototype and active engineering implementation. The current system establishes the core commercial, diagramming, production, scheduling, reporting, and communication workflows.

Further development may include:

- Authentication and role-based permissions.
- Migration from spreadsheet storage to a transactional database.
- Audit logs and record-version history.
- Inventory and raw-material management.
- Production-capacity calculations.
- Machine-status acquisition through Modbus.
- Automated delivery-risk alerts.
- Centralized deployment and update management.
- Expanded validation, testing, and error recovery.

---

<p align="center">
  <strong>From approved proforma to scheduled production — one connected operational workflow.</strong>
</p>
