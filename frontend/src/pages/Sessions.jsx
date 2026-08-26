import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import sessionService from '../services/sessionService';

const Sessions = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [subject, setSubject] = useState('');
  const [gracePeriod, setGracePeriod] = useState(5);
  const navigate = useNavigate();

  const fetchSessions = async () => {
    try {
      const data = await sessionService.getAll();
      setSessions(data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await sessionService.create({ subject, grace_period_minutes: gracePeriod });
      setIsModalOpen(false);
      setSubject('');
      fetchSessions();
    } catch (err) {
      console.error(err);
    }
  };

  const handleStart = async (id) => {
    try {
      await sessionService.start(id);
      navigate(`/sessions/${id}`);
    } catch (err) {
      console.error(err);
      alert("Could not start session. It might already be active.");
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8 border-b border-gray-200 pb-2">
        <h1 className="text-3xl font-extrabold text-sj-primary tracking-tight">Sessions</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-sj-primary text-white rounded-lg text-sm font-medium hover:bg-sj-primary/90 shadow-sm transition-all"
        >
          Create Session
        </button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-lg">
            <h2 className="text-xl font-bold mb-4">Create New Session</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={e => setSubject(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">Grace Period (minutes)</label>
                <input
                  type="number"
                  required
                  min="0"
                  value={gracePeriod}
                  onChange={e => setGracePeriod(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-sj-primary text-white rounded-lg hover:bg-sj-primary/90 shadow-sm transition-all">Submit</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-md border border-gray-200/60 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Subject</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Date</th>
              <th className="px-6 py-4 text-left text-xs font-bold text-sj-primary uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-sj-primary uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? <tr><td colSpan="4" className="p-4 text-center">Loading...</td></tr> : 
             sessions.map(session => (
              <tr key={session.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{session.subject}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(session.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    session.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                    session.status === 'COMPLETED' ? 'bg-gray-100 text-gray-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {session.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                  {session.status === 'CREATED' && (
                    <button onClick={() => handleStart(session.id)} className="text-sj-secondary hover:text-red-900 font-bold transition-colors">Start Attendance</button>
                  )}
                  {session.status === 'ACTIVE' && (
                    <Link to={`/sessions/${session.id}`} className="text-sj-primary hover:text-sj-primary/80 font-bold transition-colors">Open Attendance</Link>
                  )}
                  {session.status === 'COMPLETED' && (
                    <Link to={`/sessions/${session.id}`} className="text-gray-600 hover:text-gray-900 font-bold transition-colors">View Summary</Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Sessions;
