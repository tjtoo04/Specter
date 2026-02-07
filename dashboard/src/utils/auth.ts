import { betterAuth, jwt } from "better-auth";
import Database from "better-sqlite3";

export const auth = betterAuth({
    database: new Database("./sqlite.db"),
    plugins: [
        // jwt({
        //     jwks: {
        //         // Better Auth will expose public keys at: 
        //         // [BASE_URL]/api/auth/jwks
        //         keyPairConfig: {
        //             alg: "EdDSA", // Default high-performance algorithm
        //         },
        //     },
        // })
    ]
});
