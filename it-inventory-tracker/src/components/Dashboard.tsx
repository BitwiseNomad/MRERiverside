'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Laptop, Monitor, Smartphone, Printer, HardDrive, Menu, Plus, Search, User, Bell, Settings, LogOut, Sun, Moon } from "lucide-react"
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import Link from 'next/link'

const data = [
  { name: 'Jan', value: 1000 },
  { name: 'Feb', value: 1100 },
  { name: 'Mar', value: 1200 },
  { name: 'Apr', value: 1300 },
  { name: 'May', value: 1400 },
]

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState('')
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const handleSearch = () => {
    console.log('Searching for:', searchQuery)
  }

  const handleAddItem = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    console.log('Adding new item:', Object.fromEntries(formData))
  }

  const handleGenerateReport = () => {
    console.log('Generating inventory report')
  }

  return (
    <div className={`flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200 ${darkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <aside className="hidden w-64 bg-white dark:bg-gray-800 shadow-md lg:block transition-colors duration-200">
        <div className="p-4">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Riverside IT Inventory</h2>
        </div>
        <nav className="mt-4">
          <Link href="/" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-700">
            <Laptop className="w-5 h-5 mr-2" />
            Dashboard
          </Link>
          <Link href="/items" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
            <Monitor className="w-5 h-5 mr-2" />
            All Items
          </Link>
          <Link href="/hardware" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
            <Smartphone className="w-5 h-5 mr-2" />
            Hardware
          </Link>
          <Link href="/software" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
            <HardDrive className="w-5 h-5 mr-2" />
            Software
          </Link>
          <Link href="/reports" className="flex items-center px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700">
            <Printer className="w-5 h-5 mr-2" />
            Reports
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-800 shadow-md transition-colors duration-200">
          <div className="flex items-center">
            <Button variant="ghost" size="icon" className="mr-4 lg:hidden">
              <Menu className="w-6 h-6" />
              <span className="sr-only">Toggle Menu</span>
            </Button>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Dashboard</h1>
          </div>
          <div className="flex items-center">
            <div className="relative mr-4">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search inventory..." 
                className="pl-8 w-[300px]" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Button variant="ghost" size="icon" className="mr-2" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
            </Button>
            <Button variant="ghost" size="icon" className="mr-2">
              <Bell className="w-6 h-6" />
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <User className="w-6 h-6" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</CardTitle>
                <Laptop className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">1,234</div>
                <p className="text-xs text-green-500">+20 from last month</p>
                <div className="h-10 mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                      <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Available Items</CardTitle>
                <Monitor className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">867</div>
                <p className="text-xs text-green-500">+5 from last week</p>
                <div className="h-10 mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                      <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Low Stock Items</CardTitle>
                <HardDrive className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">24</div>
                <p className="text-xs text-red-500">+2 from yesterday</p>
                <div className="h-10 mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                      <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending Requests</CardTitle>
                <Smartphone className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">12</div>
                <p className="text-xs text-yellow-500">-3 from last week</p>
                <div className="h-10 mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                      <Line type="monotone" dataKey="value" stroke="#eab308" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mt-6">
            {/* Low Stock Alerts */}
            <Card className="col-span-2 bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Low Stock Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mr-2">
                      <div className="bg-red-600 h-2.5 rounded-full" style={{ width: '10%' }}></div>
                    </div>
                    <span className="flex-1 text-sm text-gray-600 dark:text-gray-400">Dell XPS 15 Laptops - 2 remaining</span>
                    <Button size="sm" className="bg-red-500 hover:bg-red-600 text-white">Reorder</Button>
                  </div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mr-2">
                      <div className="bg-yellow-400 h-2.5 rounded-full" style={{ width: '25%' }}></div>
                    </div>
                    <span className="flex-1 text-sm text-gray-600 dark:text-gray-400">HP LaserJet Toner Cartridges - 5 remaining</span>
                    <Button size="sm" className="bg-yellow-400 hover:bg-yellow-500 text-white">Reorder</Button>
                  </div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mr-2">
                      <div className="bg-yellow-400 h-2.5 rounded-full" style={{ width: '50%' }}></div>
                    </div>
                    <span className="flex-1 text-sm text-gray-600 dark:text-gray-400">Microsoft Office Licenses - 10 remaining</span>
                    <Button size="sm" className="bg-yellow-400 hover:bg-yellow-500 text-white">Reorder</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Add Item */}
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Quick Add Item</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddItem} className="space-y-4">
                  <Input placeholder="Item Name" name="name" required className="bg-gray-50 dark:bg-gray-700" />
                  <Input placeholder="Category" name="category" required className="bg-gray-50 dark:bg-gray-700" />
                  <Input placeholder="Serial Number" name="serialNumber" className="bg-gray-50 dark:bg-gray-700" />
                  <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Item
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Recent Activities */}
            <Card className="col-span-2 bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Recent Activities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center mr-3">
                      <Laptop className="w-4 h-4 text-green-500 dark:text-green-300" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">New laptop assigned to John Doe</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center mr-3">
                      <HardDrive className="w-4 h-4 text-blue-500 dark:text-blue-300" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Software license renewed</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">1 day ago</p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 dark:bg-yellow-800 rounded-full flex items-center justify-center mr-3">
                      <Printer className="w-4 h-4 text-yellow-500 dark:text-yellow-300" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">Maintenance scheduled for Rack #123</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">2 days ago</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Generate Report */}
            <Card className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-200">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Generate Report</CardTitle>
              </CardHeader>
              <CardContent>
                <Button onClick={handleGenerateReport} className="w-full bg-purple-500 hover:bg-purple-600 text-white">
                  Generate Inventory Report
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
