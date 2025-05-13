import React from "react";
import styles from "./Banner.module.css";
import Link from "next/link";

export default function Banner({
    heading = "Please complete your profile",
    description = "Upload your resume and let our AI match you with jobs that actually fit. Want even better results? Tweak or overwrite fields like skills or experience — it's like giving your resume a quick glow-up before it goes job hunting!",
    buttonText = "Complete Profile",
    buttonLink = "/profile",
    backgroundImage = "https://rukminim2.flixcart.com/image/850/1000/poster/v/n/t/akhuratha-poster-movie-lilo-stitch-lilo-and-stitch-hd-wallpaper-original-imaek7mzae8nwqfa.jpeg?q=90&crop=false",
}) {
    return (
        <section className={styles.main}>
            <div className={`${styles.container} ${styles.wrapper}`}>
                <div
                    className={styles.card}
                    style={{ backgroundImage: `url(${backgroundImage})` }}
                >
                    <div className={styles.overlay}>
                        <h2>{heading}</h2>
                        <p>{description}</p>
                        <Link href={buttonLink}>
                            <button>{buttonText}</button>
                        </Link>
                    </div>
                </div>
            </div>
        </section>
    );
}