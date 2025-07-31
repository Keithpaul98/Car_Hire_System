# 🏗️ System Architecture Documentation

## Overview

This document outlines the technical architecture of the Enterprise Car Hire Management System, designed for scalability, maintainability, and security.

## 🎯 Architectural Principles

### 1. Separation of Concerns
- **Backend**: Pure API service handling business logic
- **Frontend**: Presentation layer with user interaction
- **Database**: Data persistence and integrity
- **Cache**: Performance optimization layer

### 2. Scalability Patterns
- **Horizontal Scaling**: Load balancer ready
- **Database Optimization**: Proper indexing and query optimization
- **Caching Strategy**: Multi-layer caching approach
- **Microservice Ready**: Modular design for future service separation

### 3. Security by Design
- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: Server-side validation for all inputs

## 🔧 Backend Architecture

### Django Application Structure
```
backend/
├── apps/
│   ├── authentication/        # User management & auth
│   │   ├── models.py         # User, Profile models
│   │   ├── serializers.py    # API serializers
│   │   ├── views.py          # Authentication endpoints
│   │   └── permissions.py    # Custom permissions
│   ├── vehicles/             # Vehicle management
│   │   ├── models.py         # Car, Category, Feature models
│   │   ├── serializers.py    # Vehicle API serializers
│   │   ├── views.py          # Vehicle CRUD endpoints
│   │   └── filters.py        # Search and filter logic
│   ├── bookings/             # Booking system
│   │   ├── models.py         # Booking, BookingStatus models
│   │   ├── serializers.py    # Booking API serializers
│   │   ├── views.py          # Booking endpoints
│   │   └── services.py       # Business logic services
│   ├── payments/             # Payment processing
│   │   ├── models.py         # Payment, Transaction models
│   │   ├── serializers.py    # Payment API serializers
│   │   ├── views.py          # Payment endpoints
│   │   └── gateways.py       # Payment gateway integrations
│   └── core/                 # Shared utilities
│       ├── models.py         # Base models
│       ├── permissions.py    # Base permissions
│       ├── pagination.py     # Custom pagination
│       └── exceptions.py     # Custom exceptions
├── config/
│   ├── settings/             # Environment-specific settings
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Development settings
│   │   ├── production.py    # Production settings
│   │   └── testing.py       # Testing settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
└── requirements/
    ├── base.txt             # Base requirements
    ├── development.txt      # Development requirements
    └── production.txt       # Production requirements
```

### Database Design

#### Core Entities
```sql
-- Users and Authentication
Users (id, email, password_hash, first_name, last_name, phone, created_at, updated_at)
UserProfiles (user_id, date_of_birth, license_number, address, preferences)
UserRoles (id, name, permissions)
LoyaltyProgram (user_id, points_balance, tier_level, joined_date)

-- Vehicle Management
VehicleCategories (id, name, description, base_price_multiplier)
VehicleFeatures (id, name, description, icon, additional_cost)
Vehicles (id, make, model, year, category_id, license_plate, daily_rate, status, current_mileage)
VehicleImages (id, vehicle_id, image_url, is_primary, alt_text)
VehicleFeatureAssignments (vehicle_id, feature_id)
VehicleInsurance (id, vehicle_id, policy_number, provider, start_date, end_date, coverage_type)
VehicleSafetyEquipment (id, vehicle_id, equipment_type, last_checked, status, notes)
VehicleTracking (id, vehicle_id, latitude, longitude, timestamp, speed, status)

-- Booking System
Bookings (id, user_id, vehicle_id, start_date, end_date, total_cost, status, created_at)
BookingExtras (booking_id, feature_id, quantity, unit_cost)
BookingStatusHistory (booking_id, status, changed_at, changed_by, notes)
MileageLog (id, booking_id, start_mileage, end_mileage, total_distance)

-- Payment System
Payments (id, booking_id, amount, currency, status, payment_method, transaction_id)
PaymentRefunds (id, payment_id, amount, reason, processed_at)
FinancialTransactions (id, type, amount, description, payment_method, processed_at)

-- Customer Engagement
Reviews (id, user_id, vehicle_id, booking_id, rating, comment, created_at, verified)
IssueReports (id, user_id, vehicle_id, booking_id, issue_type, description, status, reported_at)
IssueVerification (id, issue_report_id, admin_id, verified_at, resolution_notes, action_taken)
Promotions (id, title, description, discount_type, discount_value, start_date, end_date, conditions)
Penalties (id, user_id, booking_id, penalty_type, amount, reason, applied_at, status)
```

#### Indexes for Performance
```sql
-- Search optimization
CREATE INDEX idx_vehicles_category_status ON vehicles(category_id, status);
CREATE INDEX idx_bookings_dates ON bookings(start_date, end_date);
CREATE INDEX idx_bookings_user_status ON bookings(user_id, status);

-- Full-text search
CREATE INDEX idx_vehicles_search ON vehicles USING gin(to_tsvector('english', make || ' ' || model));
```

### API Design Patterns

#### RESTful Endpoints
```
Authentication:
POST   /api/auth/register/          # User registration
POST   /api/auth/login/             # User login
POST   /api/auth/refresh/           # Token refresh
POST   /api/auth/logout/            # User logout

Vehicles:
GET    /api/vehicles/               # List vehicles with filters
GET    /api/vehicles/{id}/          # Vehicle details
GET    /api/vehicles/{id}/availability/ # Check availability
GET    /api/vehicles/categories/    # Vehicle categories
GET    /api/vehicles/features/      # Available features

Bookings:
GET    /api/bookings/               # User's bookings
POST   /api/bookings/               # Create booking
GET    /api/bookings/{id}/          # Booking details
PUT    /api/bookings/{id}/          # Update booking
DELETE /api/bookings/{id}/          # Cancel booking

Payments:
POST   /api/payments/               # Process payment
GET    /api/payments/{id}/          # Payment details
POST   /api/payments/{id}/refund/   # Process refund
GET    /api/financial-transactions/ # Financial transaction history

Customer Engagement:
GET    /api/reviews/                # List reviews
POST   /api/reviews/                # Create review
GET    /api/reviews/vehicle/{id}/   # Vehicle reviews
POST   /api/issues/                 # Report issue
GET    /api/issues/                 # User's reported issues
PUT    /api/issues/{id}/verify/     # Admin verify issue
GET    /api/promotions/             # Active promotions
GET    /api/loyalty/points/         # User loyalty points

Vehicle Management (Extended):
GET    /api/vehicles/{id}/tracking/ # Vehicle GPS location
GET    /api/vehicles/{id}/mileage/  # Mileage history
GET    /api/vehicles/{id}/insurance/ # Insurance details
PUT    /api/vehicles/{id}/safety-check/ # Update safety equipment
GET    /api/admin/insurance-alerts/ # Insurance expiration alerts
```

#### Response Format
```json
{
  "success": true,
  "data": {
    "id": 1,
    "make": "Toyota",
    "model": "Camry"
  },
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 20
  },
  "errors": null
}
```

## 🎨 Frontend Architecture

### Next.js Application Structure
```
frontend/
├── src/
│   ├── components/               # Reusable UI components
│   │   ├── ui/                  # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── forms/               # Form components
│   │   │   ├── SearchForm.tsx
│   │   │   └── BookingForm.tsx
│   │   ├── layout/              # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Sidebar.tsx
│   │   └── features/            # Feature-specific components
│   │       ├── vehicles/
│   │       ├── bookings/
│   │       └── auth/
│   ├── pages/                   # Next.js pages
│   │   ├── index.tsx           # Home page
│   │   ├── vehicles/           # Vehicle pages
│   │   ├── bookings/           # Booking pages
│   │   └── auth/               # Authentication pages
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useVehicles.ts
│   │   └── useBookings.ts
│   ├── services/                # API services
│   │   ├── api.ts              # Base API configuration
│   │   ├── auth.ts             # Authentication services
│   │   ├── vehicles.ts         # Vehicle services
│   │   └── bookings.ts         # Booking services
│   ├── utils/                   # Utility functions
│   │   ├── formatters.ts       # Data formatting
│   │   ├── validators.ts       # Input validation
│   │   └── constants.ts        # Application constants
│   ├── types/                   # TypeScript definitions
│   │   ├── api.ts              # API response types
│   │   ├── auth.ts             # Authentication types
│   │   └── vehicles.ts         # Vehicle types
│   └── styles/                  # Styling
│       ├── globals.css         # Global styles
│       └── components.css      # Component styles
├── public/                      # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
└── tests/                       # Test files
    ├── components/
    ├── pages/
    └── utils/
```

### Component Architecture

#### Design System Components
```typescript
// Base UI Components
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

// Feature Components
interface VehicleCardProps {
  vehicle: Vehicle;
  onSelect: (vehicle: Vehicle) => void;
  showAvailability?: boolean;
}

// Page Components
interface VehicleListPageProps {
  filters: VehicleFilters;
  onFiltersChange: (filters: VehicleFilters) => void;
}
```

#### State Management Strategy
```typescript
// React Query for server state
const useVehicles = (filters: VehicleFilters) => {
  return useQuery({
    queryKey: ['vehicles', filters],
    queryFn: () => vehicleService.getVehicles(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Context for global client state
interface AppContextType {
  user: User | null;
  theme: 'light' | 'dark';
  language: string;
}

// Local state for component-specific data
const [searchFilters, setSearchFilters] = useState<VehicleFilters>({
  category: '',
  priceRange: [0, 1000],
  features: [],
});
```

## 🔄 Data Flow Architecture

### Request Flow
```
User Action → Component → Hook → Service → API → Database
                ↓
User Interface ← Component ← Hook ← Service ← API ← Database
```

### Authentication Flow
```
1. User submits credentials
2. Frontend validates input
3. API validates credentials
4. JWT tokens generated
5. Tokens stored securely
6. Subsequent requests include token
7. Token validated on each request
```

### Booking Flow
```
1. User searches vehicles
2. System checks availability
3. User selects vehicle and dates
4. System calculates pricing
5. User confirms booking
6. Payment processing
7. Booking confirmation
8. Email notifications
```

## 🚀 Performance Architecture

### Caching Strategy
```
Level 1: Browser Cache (Static assets)
Level 2: CDN Cache (Images, CSS, JS)
Level 3: Application Cache (API responses)
Level 4: Database Cache (Query results)
Level 5: Database (Persistent storage)
```

### Database Optimization
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Proper indexing and query structure
- **Read Replicas**: Separate read and write operations
- **Partitioning**: Large table partitioning for performance

### Frontend Optimization
- **Code Splitting**: Load only necessary code
- **Lazy Loading**: Load components on demand
- **Image Optimization**: WebP format with fallbacks
- **Bundle Optimization**: Tree shaking and minification

## 🔒 Security Architecture

### Authentication & Authorization
```
JWT Token Structure:
{
  "user_id": 123,
  "email": "user@example.com",
  "roles": ["customer"],
  "exp": 1640995200,
  "iat": 1640908800
}

Permission Matrix:
- Customer: View vehicles, create bookings, manage profile
- Staff: Manage vehicles, view all bookings, customer support
- Admin: Full system access, user management, reports
```

### Data Protection
- **Encryption**: AES-256 for sensitive data
- **HTTPS**: All communications encrypted
- **Input Sanitization**: Prevent injection attacks
- **Rate Limiting**: Prevent abuse and DoS attacks

## 📊 Monitoring Architecture

### Application Monitoring
- **Error Tracking**: Centralized error logging
- **Performance Metrics**: Response times, throughput
- **User Analytics**: User behavior and conversion tracking
- **Business Metrics**: Booking rates, revenue tracking

### Infrastructure Monitoring
- **Server Metrics**: CPU, memory, disk usage
- **Database Metrics**: Query performance, connection pool
- **Network Metrics**: Bandwidth, latency
- **Security Metrics**: Failed login attempts, suspicious activity

## 🔄 Deployment Architecture

### Development Environment
```
Docker Compose:
- PostgreSQL container
- Redis container
- Django development server
- Next.js development server
```

### Production Environment
```
Load Balancer → Web Servers → Application Servers → Database
                     ↓
                Cache Layer (Redis)
                     ↓
                File Storage (S3/CDN)
```

This architecture ensures scalability, maintainability, and security while providing an excellent user experience.
