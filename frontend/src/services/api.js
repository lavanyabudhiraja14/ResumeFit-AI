/**
 * ResumeFit AI API Client Service
 */

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || '/api';
const TOKEN_KEY = 'resumefit_auth_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function getAuthHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function signup(name, email, password) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Signup failed.');
  }
  if (data.access_token) {
    setToken(data.access_token);
  }
  return data;
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Invalid email or password.');
  }
  if (data.access_token) {
    setToken(data.access_token);
  }
  return data;
}

export async function getCurrentUser() {
  const token = getToken();
  if (!token) return null;

  const res = await fetch(`${API_BASE}/users/me`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
  if (res.status === 401) {
    clearToken();
    return null;
  }
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch user profile.');
  }
  return data;
}

export async function getInterestsTaxonomy() {
  const res = await fetch(`${API_BASE}/interests`);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to load interest taxonomy.');
  }
  return data;
}

export async function getUserInterests() {
  const res = await fetch(`${API_BASE}/users/me/interests`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch user interests.');
  }
  return data;
}

export async function updateUserInterests(interests) {
  const res = await fetch(`${API_BASE}/users/me/interests`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ interests }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to save interests.');
  }
  return data;
}

export async function analyzeResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/resume/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to analyze resume file.');
  }
  return data;
}

export async function analyzeMatch(resumeSkills, jobDescription) {
  const res = await fetch(`${API_BASE}/match/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      resume_skills: resumeSkills,
      job_description: jobDescription,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to analyze job match.');
  }
  return data;
}

export async function getRecommendedJobs(params = {}) {
  const queryParams = new URLSearchParams();
  if (params.interests && params.interests.length > 0) {
    queryParams.append(
      'interests',
      Array.isArray(params.interests) ? params.interests.join(',') : params.interests
    );
  }
  if (params.location) queryParams.append('location', params.location);
  if (params.work_type && params.work_type !== 'any') queryParams.append('work_type', params.work_type);
  if (params.experience_level && params.experience_level !== 'any') queryParams.append('experience_level', params.experience_level);
  if (params.job_type && params.job_type !== 'any') queryParams.append('job_type', params.job_type);
  if (params.search) queryParams.append('search', params.search);
  if (params.min_match !== undefined && params.min_match !== null) queryParams.append('min_match', params.min_match);
  if (params.data_mode) queryParams.append('data_mode', params.data_mode);

  const queryString = queryParams.toString();
  const url = `${API_BASE}/jobs/recommended${queryString ? `?${queryString}` : ''}`;

  const res = await fetch(url, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch recommended jobs.');
  }
  return data;
}

export async function saveUserResume(filename, skills) {
  const res = await fetch(`${API_BASE}/users/me/resume`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ filename, skills }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to persist resume.');
  }
  return data;
}
