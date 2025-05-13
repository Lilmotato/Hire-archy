import React from "react";
import styles from "./CardHolder.module.css";
import JobCard from "../JobCard/JobCard";

export default function CardHolder({ jobs = [] }) {
    return (
        <section className={styles.main}>
            <div className={`${styles.container} ${styles.wrapper}`}>
                {jobs.map((job, idx) => (
                    <JobCard
                        key={idx}
                        jobTitle={job.title}
                        companyName={job.company_name}
                        companyLogo={job.companyLogo}
                        location={job.location}
                        experience={job.experience_required}
                        keySkills={job.key_skills}
                        detailsLink={job.id}
                        highlighted={job.highlighted}
                        backgroundImage={job.backgroundImage}
                        percentageMatch={job.score}
                    />
                ))}
            </div>
        </section>
    );
}