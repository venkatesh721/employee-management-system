export const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'terminated', label: 'Terminated' },
]

export const POSITION_OPTIONS = [
  { value: 'junior', label: 'Junior' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
  { value: 'manager', label: 'Manager' },
  { value: 'director', label: 'Director' },
]

export const DEPARTMENT_COLORS = {
  Engineering: '#4f46e5',
  Marketing: '#f59e0b',
  Sales: '#22c55e',
  HR: '#ef4444',
  Finance: '#06b6d4',
  Operations: '#8b5cf6',
  Legal: '#ec4899',
  Support: '#14b8a6',
}

export const ATTENDANCE_STATUS = {
  present: { label: 'Present', color: '#22c55e' },
  absent: { label: 'Absent', color: '#ef4444' },
  late: { label: 'Late', color: '#f59e0b' },
  half_day: { label: 'Half Day', color: '#8b5cf6' },
  leave: { label: 'On Leave', color: '#64748b' },
}

export const PAGE_SIZE = 10
