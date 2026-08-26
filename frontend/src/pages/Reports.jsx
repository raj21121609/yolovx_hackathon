import React, { useState, useEffect } from 'react';
import { Download, AlertTriangle, FileText, Search } from 'lucide-react';
import { reportService } from '../services/reportService';

function Reports() {
  const [history, setHistory] = useState([]);
  const [lowAttendance, setLowAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('history');
  
  // Filters
  const [filterDate, setFilterDate] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchData();
  }, [filterDate, filterStatus]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [histData, lowData] = await Promise.all([
        reportService.getHistory({ date: filterDate, status: filterStatus }),
        reportService.getLowAttendance()
      ]);
      setHistory(histData);
      setLowAttendance(lowData);
    } catch (error) {
      console.error("Failed to fetch reports", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center border-b border-gray-200 pb-2">
        <h1 className="text-3xl font-extrabold text-sj-primary tracking-tight">Reports & Analytics</h1>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('history')}
            className={`${
              activeTab === 'history'
                ? 'border-sj-primary text-sj-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-bold text-sm flex items-center transition-colors`}
          >
            <FileText size={18} className="mr-2" />
            Attendance History
          </button>
          <button
            onClick={() => setActiveTab('low-attendance')}
            className={`${
              activeTab === 'low-attendance'
                ? 'border-sj-primary text-sj-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-bold text-sm flex items-center transition-colors`}
          >
            <AlertTriangle size={18} className="mr-2" />
            Low Attendance Warning
          </button>
        </nav>
      </div>

      {loading && <div className="text-gray-500">Loading data...</div>}

      {/* History Tab */}
      {!loading && activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100 bg-gray-50 flex gap-4 items-center">
            <div className="flex-1 max-w-xs">
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Filter Date</label>
              <input
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex-1 max-w-xs">
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">All Statuses</option>
                <option value="PRESENT">Present</option>
                <option value="LATE">Late</option>
                <option value="ABSENT">Absent</option>
              </select>
            </div>
            <div className="mt-5">
              <button 
                onClick={() => { setFilterDate(''); setFilterStatus(''); }}
                className="text-sm text-indigo-600 hover:text-indigo-900 font-medium"
              >
                Clear Filters
              </button>
            </div>
          </div>
          
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Student</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Subject</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Date</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{record.student_name}</div>
                    <div className="text-gray-500 text-xs">{record.roll_number}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.subject}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(record.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      record.status === 'PRESENT' ? 'bg-green-100 text-green-800' :
                      record.status === 'LATE' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                    No attendance records found matching filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Low Attendance Tab */}
      {!loading && activeTab === 'low-attendance' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100 bg-red-50">
            <h3 className="text-lg font-medium text-red-800 flex items-center">
              <AlertTriangle className="mr-2" size={20} />
              Students below 75% Attendance
            </h3>
            <p className="text-sm text-red-600 mt-1">These students may require intervention.</p>
          </div>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Student Name</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Roll Number</th>
                <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Attendance %</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {lowAttendance.map((student) => (
                <tr key={student.student_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{student.student_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.roll_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-3 py-1 inline-flex text-sm font-bold rounded-full bg-red-100 text-red-800">
                      {student.attendance_percentage}%
                    </span>
                  </td>
                </tr>
              ))}
              {lowAttendance.length === 0 && (
                <tr>
                  <td colSpan="3" className="px-6 py-8 text-center text-gray-500">
                    Excellent! No students have low attendance.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Reports;
