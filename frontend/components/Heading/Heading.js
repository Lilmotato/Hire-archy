import styles from "./Heading.module.css";

export default function Heading({ backgroundImageName, fontSize, heading, subheading, hr }) {
    return (
        (heading || subheading) && (
            <section className={styles.main}>
                {heading && (
                    <h1
                        className={`${styles.heading}`}
                        style={{
                            backgroundImage:
                                backgroundImageName || 'url("https://cdn.dribbble.com/users/4025749/screenshots/7319596/media/e8e15b54c947cdc39e9abe93a9080e73.gif")',
                                fontSize: fontSize || "300%",
                        }}
                    >
                        {heading}
                    </h1>
                )}
                {subheading && <p className={styles.subheading}>{subheading}</p>}
                {hr && <hr />}
            </section>
        )
    );
}