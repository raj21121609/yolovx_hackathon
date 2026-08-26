import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, CheckCircle, Clock } from 'lucide-react';
import { reportService } from '../services/reportService';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const result = await reportService.getDashboard();
        setData(result);
      } catch (err) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <div className="p-8">Loading dashboard...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  const chartData = [
    { name: 'Present', value: data.present_today, color: '#10b981' },
    { name: 'Late', value: data.late_today, color: '#f59e0b' },
    { name: 'Absent', value: data.absent_today, color: '#ef4444' }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center pb-2 border-b border-gray-200">
        <h1 className="text-3xl font-extrabold text-sj-primary tracking-tight">Dashboard Overview</h1>
        <div className="space-x-4">
          <Link to="/sessions" className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 text-gray-700 shadow-sm transition-all">
            Sessions
          </Link>
          <Link to="/reports" className="px-4 py-2 bg-sj-primary text-white rounded-lg text-sm font-medium hover:bg-sj-primary/90 shadow-sm transition-all">
            View Reports
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex items-center space-x-4 transition-transform hover:-translate-y-1">
          <div className="p-3 bg-blue-50 text-sj-primary rounded-lg">
            <Calendar size={26} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Today's Sessions</p>
            <p className="text-3xl font-bold text-gray-900">{data.today_sessions}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex items-center space-x-4 transition-transform hover:-translate-y-1">
          <div className="p-3 bg-blue-50 text-sj-primary rounded-lg">
            <Users size={26} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Total Students</p>
            <p className="text-3xl font-bold text-gray-900">{data.total_students}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex items-center space-x-4 transition-transform hover:-translate-y-1">
          <div className="p-3 bg-green-50 text-green-600 rounded-lg">
            <CheckCircle size={26} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Present Today</p>
            <p className="text-3xl font-bold text-gray-900">{data.present_today + data.late_today}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex items-center space-x-4 transition-transform hover:-translate-y-1">
          <div className="p-3 bg-blue-50 text-sj-primary rounded-lg">
            <Clock size={26} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Avg Attendance</p>
            <p className="text-3xl font-bold text-gray-900">{data.average_attendance}%</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
        <h2 className="text-lg font-bold mb-6 text-sj-primary uppercase tracking-wide">Today's Attendance Distribution</h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6b7280'}} dy={10} />
              <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{fill: '#6b7280'}} />
              <Tooltip cursor={{fill: '#f3f4f6'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={60}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
