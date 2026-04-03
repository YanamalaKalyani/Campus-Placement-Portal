"use client"

import { useState, useEffect } from "react"

type UserRole = "admin" | "student" | "company" | null
type Page = "landing" | "login" | "register" | "dashboard"

interface User {
  name: string
  email: string
  role: UserRole
  avatar?: string
}

export default function CampusPlacementPortal() {
  const [currentPage, setCurrentPage] = useState<Page>("landing")
  const [currentRole, setCurrentRole] = useState<UserRole>(null)
  const [user, setUser] = useState<User | null>(null)
  const [activeSidebarItem, setActiveSidebarItem] = useState("dashboard")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogin = (role: UserRole) => {
    setCurrentRole(role)
    setCurrentPage("login")
  }

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Demo login - set user based on role
    const demoUsers: Record<string, User> = {
      admin: { name: "Super Admin", email: "admin@campus.edu", role: "admin" },
      student: { name: "Priti Bhadja", email: "priti@campus.edu", role: "student" },
      company: { name: "Google", email: "hr@google.com", role: "company" },
    }
    if (currentRole) {
      setUser(demoUsers[currentRole])
      setCurrentPage("dashboard")
    }
  }

  const handleLogout = () => {
    setUser(null)
    setCurrentRole(null)
    setCurrentPage("landing")
    setActiveSidebarItem("dashboard")
  }

  const getSidebarItems = () => {
    switch (user?.role) {
      case "admin":
        return [
          { id: "dashboard", label: "Dashboard", icon: DashboardIcon },
          { id: "companies", label: "Companies", icon: CompaniesIcon },
          { id: "students", label: "Students", icon: StudentsIcon },
          { id: "stats", label: "Placement Stats", icon: StatsIcon },
          { id: "placements", label: "Manage Placements", icon: PlacementsIcon },
          { id: "drives", label: "Placement Drives", icon: DrivesIcon },
          { id: "notifications", label: "Notifications", icon: NotificationsIcon },
        ]
      case "student":
        return [
          { id: "dashboard", label: "Dashboard", icon: DashboardIcon },
          { id: "companies", label: "Companies", icon: CompaniesIcon },
          { id: "profile", label: "My Profile", icon: ProfileIcon },
          { id: "applications", label: "Applications", icon: ApplicationsIcon },
          { id: "notifications", label: "Notifications", icon: NotificationsIcon },
        ]
      case "company":
        return [
          { id: "dashboard", label: "Dashboard", icon: DashboardIcon },
          { id: "applications", label: "Applications", icon: ApplicationsIcon },
          { id: "students", label: "Student Profiles", icon: StudentsIcon },
          { id: "profile", label: "Company Profile", icon: ProfileIcon },
          { id: "analytics", label: "Analytics", icon: StatsIcon },
        ]
      default:
        return []
    }
  }

  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#1e3a5f] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (currentPage === "landing") {
    return <LandingPage onLogin={handleLogin} />
  }

  if (currentPage === "login") {
    return (
      <LoginPage role={currentRole} onSubmit={handleLoginSubmit} onBack={() => setCurrentPage("landing")} />
    )
  }

  if (currentPage === "dashboard" && user) {
    return (
      <DashboardLayout
        user={user}
        sidebarItems={getSidebarItems()}
        activeSidebarItem={activeSidebarItem}
        onSidebarItemClick={setActiveSidebarItem}
        onLogout={handleLogout}
      >
        {user.role === "admin" && <AdminDashboard activeItem={activeSidebarItem} />}
        {user.role === "student" && <StudentDashboard activeItem={activeSidebarItem} user={user} />}
        {user.role === "company" && <CompanyDashboard activeItem={activeSidebarItem} user={user} />}
      </DashboardLayout>
    )
  }

  return null
}

// Icons
function DashboardIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7"></rect>
      <rect x="14" y="3" width="7" height="7"></rect>
      <rect x="14" y="14" width="7" height="7"></rect>
      <rect x="3" y="14" width="7" height="7"></rect>
    </svg>
  )
}

function CompaniesIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
      <polyline points="9 22 9 12 15 12 15 22"></polyline>
    </svg>
  )
}

function StudentsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
      <circle cx="9" cy="7" r="4"></circle>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
    </svg>
  )
}

function StatsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="20" x2="18" y2="10"></line>
      <line x1="12" y1="20" x2="12" y2="4"></line>
      <line x1="6" y1="20" x2="6" y2="14"></line>
    </svg>
  )
}

function PlacementsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
      <path d="M9 14l2 2 4-4"></path>
    </svg>
  )
}

function DrivesIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
  )
}

function NotificationsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
    </svg>
  )
}

function ProfileIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
  )
}

function ApplicationsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
    </svg>
  )
}

function LogoutIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
      <polyline points="16 17 21 12 16 7"></polyline>
      <line x1="21" y1="12" x2="9" y2="12"></line>
    </svg>
  )
}

// Landing Page
function LandingPage({ onLogin }: { onLogin: (role: UserRole) => void }) {
  return (
    <div className="min-h-screen bg-[#f8f9fa] flex flex-col items-center justify-center p-8">
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-[#1e3a5f] rounded-xl flex items-center justify-center mx-auto mb-6">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
            <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-[#8b1538] mb-2">Campus Placement Portal</h1>
        <p className="text-gray-600">Connecting talent with opportunity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
        <LoginCard
          icon={
            <div className="w-12 h-12 bg-[#1e3a5f] rounded-full flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
            </div>
          }
          title="Admin Login"
          description="Manage companies, students, and placements"
          onClick={() => onLogin("admin")}
        />
        <LoginCard
          icon={
            <div className="w-12 h-12 bg-[#c9302c] rounded-full flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
          }
          title="Student Login"
          description="Apply to companies and track your progress"
          onClick={() => onLogin("student")}
        />
        <LoginCard
          icon={
            <div className="w-12 h-12 bg-[#2e7d32] rounded-full flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
            </div>
          }
          title="Company Login"
          description="Recruit talent and manage placements"
          onClick={() => onLogin("company")}
        />
      </div>
    </div>
  )
}

function LoginCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode
  title: string
  description: string
  onClick: () => void
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center hover:shadow-md transition-shadow">
      <div className="flex justify-center mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>
      <button
        onClick={onClick}
        className="text-[#8b1538] font-medium flex items-center justify-center gap-1 mx-auto hover:gap-2 transition-all"
      >
        Continue
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </button>
    </div>
  )
}

// Login Page
function LoginPage({
  role,
  onSubmit,
  onBack,
}: {
  role: UserRole
  onSubmit: (e: React.FormEvent) => void
  onBack: () => void
}) {
  const roleColors: Record<string, string> = {
    admin: "#1e3a5f",
    student: "#c9302c",
    company: "#2e7d32",
  }

  const roleLabels: Record<string, string> = {
    admin: "Admin",
    student: "Student",
    company: "Company",
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center p-8">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <button onClick={onBack} className="text-gray-500 hover:text-gray-700 mb-4 flex items-center gap-1">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Back
        </button>

        <div className="text-center mb-8">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
            style={{ backgroundColor: roleColors[role || "admin"] }}
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">{roleLabels[role || "admin"]} Login</h2>
          <p className="text-gray-600">Sign in to access your dashboard</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              defaultValue={`demo@${role}.com`}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#8b1538] focus:border-transparent outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              defaultValue="demo123"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#8b1538] focus:border-transparent outline-none"
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 bg-[#8b1538] text-white font-medium rounded-lg hover:bg-[#6d102c] transition-colors"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}

// Dashboard Layout
function DashboardLayout({
  user,
  sidebarItems,
  activeSidebarItem,
  onSidebarItemClick,
  onLogout,
  children,
}: {
  user: User
  sidebarItems: { id: string; label: string; icon: () => React.ReactNode }[]
  activeSidebarItem: string
  onSidebarItemClick: (id: string) => void
  onLogout: () => void
  children: React.ReactNode
}) {
  const sidebarColors: Record<string, { bg: string; active: string }> = {
    admin: { bg: "#1e3a5f", active: "#8b1538" },
    student: { bg: "#1e3a5f", active: "#8b1538" },
    company: { bg: "#1e3a5f", active: "#2e7d32" },
  }

  const colors = sidebarColors[user.role || "admin"]

  return (
    <div className="flex min-h-screen bg-[#f8f9fa]">
      {/* Sidebar */}
      <aside className="w-64 text-white flex flex-col" style={{ backgroundColor: colors.bg }}>
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#c9302c] rounded-lg flex items-center justify-center text-white font-bold">
              {user.name.charAt(0)}
            </div>
            <div>
              <h2 className="font-semibold text-sm">Campus Portal</h2>
              <span className="text-xs text-white/70 capitalize">{user.role} Dashboard</span>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onSidebarItemClick(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left ${
                activeSidebarItem === item.id
                  ? "text-white"
                  : "text-white/70 hover:text-white hover:bg-white/10"
              }`}
              style={activeSidebarItem === item.id ? { backgroundColor: colors.active } : {}}
            >
              <item.icon />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-[#c9302c] hover:bg-white/10 transition-colors"
          >
            <LogoutIcon />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 capitalize">{activeSidebarItem}</h1>
            <p className="text-sm text-gray-600">
              {activeSidebarItem === "dashboard"
                ? "View key metrics and placement overview"
                : `Manage ${activeSidebarItem}`}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Welcome, {user.name}</p>
              <p className="text-xs text-gray-500 capitalize">{user.role}</p>
            </div>
            <div className="w-10 h-10 bg-[#1e3a5f] rounded-full flex items-center justify-center text-white font-medium">
              {user.name.charAt(0)}
            </div>
          </div>
        </header>

        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}

// Admin Dashboard
function AdminDashboard({ activeItem }: { activeItem: string }) {
  if (activeItem === "dashboard") {
    return (
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard icon={<CompaniesIcon />} label="Registered Companies" value="2" color="blue" />
          <StatCard icon={<StudentsIcon />} label="Registered Students" value="3" color="purple" />
          <StatCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            }
            label="Placed Students"
            value="60"
            color="green"
          />
          <StatCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            }
            label="Avg Package"
            value="14.5L"
            color="yellow"
            prefix="Rs."
          />
        </div>

        {/* Branch-wise Placement & Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Branch-wise Placement</h3>
            <div className="space-y-4">
              <ProgressItem label="CSE" value={53} />
              <ProgressItem label="ECE" value={46} />
              <ProgressItem label="Mechanical" value={51} />
              <ProgressItem label="Civil" value={38} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Placement Status</h3>
            <div className="flex items-center justify-center gap-12 py-8">
              <div className="text-center">
                <p className="text-4xl font-bold text-[#2e7d32]">60</p>
                <p className="text-sm text-gray-600">Placed</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-[#c9302c]">190</p>
                <p className="text-sm text-gray-600">Unplaced</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 capitalize">{activeItem}</h3>
      <p className="text-gray-600">Content for {activeItem} section</p>
    </div>
  )
}

// Student Dashboard
function StudentDashboard({ activeItem, user }: { activeItem: string; user: User }) {
  if (activeItem === "dashboard") {
    return (
      <div className="space-y-6">
        <p className="text-gray-600">Your placement journey at a glance</p>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p className="text-sm text-gray-600 mb-1">My Applications</p>
            <p className="text-3xl font-bold text-[#1e3a5f]">5</p>
            <p className="text-xs text-gray-500">Applied to companies</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p className="text-sm text-gray-600 mb-1">Current CGPA</p>
            <p className="text-3xl font-bold text-[#2563eb]">8.2</p>
            <p className="text-xs text-gray-500">Out of 10.0</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p className="text-sm text-gray-600 mb-1">Status</p>
            <p className="text-3xl font-bold text-[#2e7d32]">Placed</p>
            <p className="text-xs text-gray-500">Offer received</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p className="text-sm text-gray-600 mb-1">Package Offered</p>
            <p className="text-3xl font-bold text-[#2e7d32]">Rs.18L</p>
            <p className="text-xs text-gray-500">CTC per annum</p>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Placement Statistics</h3>
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600">Campus Placement Ratio</span>
              <span className="text-[#2e7d32] font-semibold">24.0%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div className="bg-[#1e3a5f] h-2 rounded-full" style={{ width: "24%" }}></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>60 Placed</span>
              <span>190 Unplaced</span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-[#1e3a5f]">250</p>
                <p className="text-xs text-gray-500">Total Students</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-[#2563eb]">Rs.14.5L</p>
                <p className="text-xs text-gray-500">Avg Package</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-[#c9302c]">Rs.40L</p>
                <p className="text-xs text-gray-500">Highest Package</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Branch-wise Placement</h3>
            <div className="space-y-4">
              <ProgressItem label="CSE" value={53} subtext="43/80 students" />
              <ProgressItem label="ECE" value={46} subtext="32/70 students" />
              <ProgressItem label="Mechanical" value={51} subtext="23/45 students" />
              <ProgressItem label="Civil" value={38} subtext="21/55 students" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 capitalize">{activeItem}</h3>
      <p className="text-gray-600">Content for {activeItem} section</p>
    </div>
  )
}

// Company Dashboard
function CompanyDashboard({ activeItem, user }: { activeItem: string; user: User }) {
  if (activeItem === "students") {
    return (
      <div className="space-y-6">
        <p className="text-gray-600">Browse eligible student candidates</p>

        <div className="bg-[#f0f9ff] border border-[#bae6fd] rounded-lg px-4 py-2 inline-block">
          <span className="text-[#1e3a5f]">Total Registered Students: </span>
          <strong className="text-[#c9302c]">3</strong>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: "priti bhadja", enrollment: "12302040701139", cgpa: "8.00", branch: "CE", email: "pritibhadja@gmail.com", phone: "8347758215" },
            { name: "om panchal", enrollment: "12302040701023", cgpa: "N/A", branch: "Not specified", email: "ompanchal@gmail.com" },
            { name: "Bhargi Antala", enrollment: "12302040701026", cgpa: "N/A", branch: "Not specified", email: "bhargi@gmail.com" },
          ].map((student, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h4 className="font-semibold text-gray-900">{student.name}</h4>
              <p className="text-xs text-gray-500 mb-4">{student.enrollment}</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">CGPA:</span>
                  <span className="text-gray-900">{student.cgpa}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Branch:</span>
                  <span className="text-gray-900">{student.branch}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Email:</span>
                  <span className="text-gray-900 text-xs">{student.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Skills:</span>
                  <span className="text-gray-900">Not specified</span>
                </div>
                {student.phone && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Phone:</span>
                    <span className="text-gray-900">{student.phone}</span>
                  </div>
                )}
              </div>
              <button className="w-full mt-4 py-2 bg-[#c9302c] text-white rounded-lg hover:bg-[#a52722] transition-colors">
                View Profile
              </button>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (activeItem === "dashboard") {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard icon={<ApplicationsIcon />} label="Total Applications" value="24" color="blue" />
          <StatCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            }
            label="Selected Students"
            value="8"
            color="green"
          />
          <StatCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            }
            label="Pending Review"
            value="12"
            color="yellow"
          />
          <StatCard icon={<DrivesIcon />} label="Active Drives" value="2" color="red" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 capitalize">{activeItem}</h3>
      <p className="text-gray-600">Content for {activeItem} section</p>
    </div>
  )
}

// Reusable Components
function StatCard({
  icon,
  label,
  value,
  color,
  prefix,
}: {
  icon: React.ReactNode
  label: string
  value: string
  color: "blue" | "purple" | "green" | "yellow" | "red"
  prefix?: string
}) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    green: "bg-green-50 text-green-600",
    yellow: "bg-yellow-50 text-yellow-600",
    red: "bg-red-50 text-red-600",
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${colors[color]}`}>{icon}</div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">
        {prefix}
        {value}
      </p>
    </div>
  )
}

function ProgressItem({ label, value, subtext }: { label: string; value: number; subtext?: string }) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="text-gray-900 font-medium">{value}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-[#1e3a5f] h-2 rounded-full" style={{ width: `${value}%` }}></div>
      </div>
      {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
    </div>
  )
}
