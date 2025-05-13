'use client';
import React, { useState } from 'react';
import styles from './CandidateFilter.module.css';
import CandidateCard from '../CandidateCard/CandidateCard';

export default function CandidateFilter() {
    const [skills, setSkills] = useState(['']);
    const [location, setLocation] = useState('');
    const [minExperience, setMinExperience] = useState('');
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSkillChange = (index, value) => {
        const updated = [...skills];
        updated[index] = value;
        setSkills(updated);
    };

    const addSkillField = () => setSkills([...skills, '']);
    const removeSkillField = (index) => {
        const updated = skills.filter((_, i) => i !== index);
        setSkills(updated);
    };

    const fetchCandidates = async () => {
        const url = new URL("http://localhost:8000/candidates/");
        skills.filter(Boolean).forEach(skill => url.searchParams.append("skills", skill));
        if (location) url.searchParams.append("location", location);
        if (minExperience) url.searchParams.append("min_experience", minExperience);

        setLoading(true);
        try {
            const res = await fetch(url.toString(), {
                method: 'GET',
                headers: { 'accept': 'application/json' }
            });
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            const data = await res.json();
            setCandidates(data);
        } catch (err) {
            console.error('Failed to fetch candidates:', err);
            setCandidates([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.filterContainer}>
            <h3 className={styles.heading}>Filter Candidates</h3>

            <div className={styles.inputRow}>
                {skills.map((skill, index) => (
                    <div key={index} className={styles.inlineGroup}>
                        <input
                            type="text"
                            value={skill}
                            placeholder="Skill"
                            onChange={(e) => handleSkillChange(index, e.target.value)}
                            className={styles.input}
                        />
                        {skills.length > 1 && (
                            <button type="button" onClick={() => removeSkillField(index)} className={styles.removeBtn}>
                                ×
                            </button>
                        )}
                    </div>
                ))}
                <button type="button" onClick={addSkillField} className={styles.addBtn}>
                    + Skill
                </button>

                <input
                    type="text"
                    placeholder="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className={styles.input}
                />

                <input
                    type="number"
                    placeholder="Min Exp"
                    value={minExperience}
                    onChange={(e) => setMinExperience(e.target.value)}
                    className={styles.input}
                />

                <button type="button" onClick={fetchCandidates} className={styles.searchBtn} disabled={loading}>
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </div>

            <div className={styles.results}>
                {candidates.length > 0 && (
                    <>
                        <h4>Results:</h4>
                        <div className={styles.cardList}>
                            {candidates.map((candidate, idx) => (
                                <CandidateCard
                                    key={idx}
                                    name={candidate.full_name}
                                    email={candidate.email}
                                    resumeLink={candidate.resume_url}
                                    keySkills={candidate.key_skills || []}
                                    location={candidate.location}
                                    experience={candidate.years_of_experience}
                                    profilePhoto={candidate.profilePhoto || null}
                                    score={candidate.score || null}
                                />
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
