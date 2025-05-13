import React from "react";
import styles from "./CandidateCard.module.css";

export default function CandidateCard({
    name,
    email,
    resumeLink,
    keySkills = [],
    location,
    experience,
    profilePhoto,
    score = null, // 🆕 Match score prop
}) {
    return (
        <section className={styles.main}>
            <div className={`${styles.container} ${styles.wrapper}`}>
                <div className={styles.card}>
                    <div className={styles.photoSection}>
                        <img
                            src={`https://api.dicebear.com/7.x/initials/svg?seed=${name}`}
                            alt={`${name}'s photo`}
                            className={styles.photo}
                        />
                    </div>
                    <div className={styles.detailsSection}>
                        <h2 className={styles.name}>
                            {name}
                            {score !== null && (
                                <span className={styles.matchScore}>
                                    &nbsp;— {Math.round(score * 100)}% Match
                                </span>
                            )}
                        </h2>
                        <p>
                            <strong>Email:</strong> {email}
                        </p>
                        <p>
                            <strong>Location:</strong> {location}
                        </p>
                        <p>
                            <strong>Experience:</strong> {experience} years
                        </p>
                        <p>
                            <strong>Resume:</strong>{" "}
                            <a href={resumeLink} target="_blank" rel="noopener noreferrer">
                                View Resume
                            </a>
                        </p>
                        <div className={styles.skills}>
                            {keySkills.map((skill, idx) => (
                                <span key={idx} className={styles.skill}>
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
