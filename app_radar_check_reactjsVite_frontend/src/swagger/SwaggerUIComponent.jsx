import React from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

const SwaggerUIComponent = () => {
  return <SwaggerUI url="/openapi_spec.json" />;
};

export default SwaggerUIComponent;
